import time
import logging
logger = logging.getLogger('peachy')
from peachyprinter.domain.commands import *
from peachyprinter.infrastructure.commander import NullCommander
from threading import Lock


class LayerWriter():

    def __init__(self,
                 disseminator,
                 path_to_points,
                 laser_control,
                 state,
                 move_distance_to_ignore=0.00001,
                 override_draw_speed=None,
                 override_move_speed=None,
                 wait_speed=None,
                 post_fire_delay_speed=None,
                 slew_delay_speed=None,
                 ):
        self._post_fire_delay_speed = post_fire_delay_speed
        self._slew_delay_speed = slew_delay_speed
        self._override_draw_speed = override_draw_speed
        self._override_move_speed = override_move_speed
        self._move_distance_to_ignore = move_distance_to_ignore
        self._state = state
        self._disseminator = disseminator
        self._path_to_points = path_to_points
        self._laser_control = laser_control
        self.laser_off_override = False
        self._after_move_wait_speed = wait_speed
        logger.info("Wait Speed: %s" % self._after_move_wait_speed)

        self._abort_current_command = False
        self._shutting_down = False
        self._shutdown = False
        self._lock = Lock()

    def _almost_equal(self, a, b):
        return (a == b or (abs(a - b) <= self._move_distance_to_ignore))

    def _same_posisition(self, pos_1, pos_2):
        return self._almost_equal(pos_1[0], pos_2[0]) and self._almost_equal(pos_1[1], pos_2[1])

    def process_layer(self, layer):
        if self._shutting_down or self._shutdown:
            raise Exception("LayerWriter already shutdown")
        min_x, max_x, min_y, max_y, layer_height = None, None, None, None, None
        with self._lock:
            if self._disseminator:
                self._disseminator.next_layer(layer.z)
            for command in layer.commands:
                # logger.info("Processing command: %s" % command)
                if self._shutting_down:
                    break
                if self._abort_current_command:
                    logger.info("Aborting Current Command")
                    self._abort_current_command = False
                    break
                if type(command) == LateralDraw:
                    if layer_height is None:
                        min_x = command.start[0]
                        max_x = command.start[0]
                        min_y = command.start[1]
                        max_y = command.start[1]
                        layer_height = layer.z
                    x, y = command.start
                    min_x = x if x < min_x else min_x
                    max_x = x if x > max_x else max_x
                    min_y = y if y < min_y else min_y
                    max_y = y if y > max_y else max_y
                    x, y = command.end
                    min_x = x if x < min_x else min_x
                    max_x = x if x > max_x else max_x
                    min_y = y if y < min_y else min_y
                    max_y = y if y > max_y else max_y
                    if not self._same_posisition(self._state.xy, command.start):
                        self._move_lateral(
                            command.start, layer.z, command.speed)
                    self._draw_lateral(command.end, layer.z, command.speed)
        return [[min_x, max_x], [min_y, max_y], layer_height]

    def _move_lateral(self, (to_x, to_y), to_z, speed):
        if self._override_move_speed:
            speed = self._override_move_speed
        laser_was_on = self._laser_control.laser_is_on()
        if laser_was_on and self._slew_delay_speed:
            self._write_lateral(
                self._state.x, self._state.y, self._state.z, self._slew_delay_speed)
        self._laser_control.set_laser_off()
        self._write_lateral(to_x, to_y, to_z, speed)
        if self._after_move_wait_speed:
            self._write_lateral(
                to_x, to_y, to_z, self._after_move_wait_speed)

    def _draw_lateral(self, (to_x, to_y), to_z, speed):
        if self._override_draw_speed:
            speed = self._override_draw_speed
        laser_was_off = not self._laser_control.laser_is_on()
        if self.laser_off_override:
            self._laser_control.set_laser_off()
        else:
            self._laser_control.set_laser_on()
        if laser_was_off and self._post_fire_delay_speed:
            self._write_lateral(
                self._state.x, self._state.y, self._state.z, self._post_fire_delay_speed)
        self._write_lateral(to_x, to_y, to_z, speed)

    def _write_lateral(self, to_x, to_y, to_z, speed):
        to_xyz = [to_x, to_y, to_z]
        path = self._path_to_points.process(self._state.xyz, to_xyz, speed)
        if self._disseminator:
            self._disseminator.process(path)
        self._state.set_state(to_xyz, speed)

    def abort_current_command(self):
        self._abort_current_command = True
        with self._lock:
            self._state.set_state((0.0, 0.0, self._state.z), self._state.speed)

    def wait_till_time(self, wait_time):
        while time.time() <= wait_time:
            if self._shutting_down:
                return
            self._move_lateral(
                self._state.xy, self._state.z, self._state.speed)

    def terminate(self):
        self._shutting_down = True
        with self._lock:
            self._shutdown = True
            try:
                if self._disseminator:
                    self._disseminator.close()
                logger.info("Layer writer shutdown correctly")
            except Exception as ex:
                logger.error(ex)


class LayerProcessing():

    def __init__(self,
                 writer,
                 state,
                 status,
                 zaxis=None,
                 max_lead_distance=0.0,
                 commander=NullCommander(),
                 pre_layer_delay=0.0,
                 layer_start_command=None,
                 layer_ended_command=None,
                 print_ended_command=None,
                 print_start_command=None,
                 dripper_on_command=None,
                 dripper_off_command=None
                 ):
        self._writer = writer
        self._layer_count = 0
        self._state = state
        self._status = status
        self._zaxis = zaxis
        self._max_lead_distance = max_lead_distance
        self._commander = commander
        self._pre_layer_delay = pre_layer_delay
        self._layer_start_command = layer_start_command
        self._layer_ended_command = layer_ended_command
        self._print_start_command = print_start_command
        self._print_ended_command = print_ended_command
        self._dripper_on_command = dripper_on_command
        self._dripper_off_command = dripper_off_command
        self._abort_current_command = False

        self._shutting_down = False
        self._shutdown = False
        self._lock = Lock()

    def process(self, layer):
        if self._shutting_down or self._shutdown:
            raise Exception("LayerProcessing already shutdown")
        with self._lock:
            if self._layer_count == 0:
                self._commander.send_command(self._print_start_command)
            self._layer_count += 1
            ahead_by = 0
            self._status.add_layer()
            self._status.set_model_height(layer.z)
            if self._zaxis:
                self._zaxis.move_to(layer.z + self._max_lead_distance / 2.0)
                self._wait_till(layer.z)
                ahead_by = self._zaxis.current_z_location_mm() - layer.z
            if self._should_process(ahead_by):
                self._commander.send_command(self._layer_start_command)
                if self._pre_layer_delay:
                    self._writer.wait_till_time(
                        time.time() + self._pre_layer_delay)
                self._status.add_axis_data(self._writer.process_layer(layer))
                self._commander.send_command(self._layer_ended_command)
            else:
                logger.warning('Dripping too fast, Skipping layer')
                self._status.skipped_layer()

    def abort_current_command(self):
        self._abort_current_command = True
        self._writer.abort_current_command()
        with self._lock:
            self._state.set_state((0.0, 0.0, self._state.z), self._state.speed)
        self._abort_current_command = False

    def _should_process(self, ahead_by_distance):
        if not ahead_by_distance:
            return True
        if (ahead_by_distance <= self._max_lead_distance):
            logger.info("Ahead (Acceptable) by: %s" % ahead_by_distance)
            return True
        logger.info("Ahead (Unacceptably) by: %s" % ahead_by_distance)
        return False

    def _wait_till(self, height):
        while self._zaxis.current_z_location_mm() < height:
            if self._shutting_down or self._abort_current_command:
                return
            if not self._status.waiting_for_drips:
                self._commander.send_command(self._dripper_on_command)
            self._status.set_waiting_for_drips()
            self._writer.wait_till_time(time.time() + (0.1))
        if self._status.waiting_for_drips:
            self._commander.send_command(self._dripper_off_command)
        self._status.set_not_waiting_for_drips()

    def terminate(self):
        self._shutting_down = True
        with self._lock:
            self._shutdown = True
            self._commander.send_command(self._print_ended_command)
            if self._zaxis:
                try:
                    self._zaxis.close()
                    logger.info("Zaxis shutdown correctly")
                except Exception as ex:
                    logger.error(ex)
            try:
                self._commander.close()
                logger.info("Commander shutdown correctly")
            except Exception as ex:
                logger.error(ex)
