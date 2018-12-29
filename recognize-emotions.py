#!/usr/bin/env python3
#
# Copyright 2018 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import functools
import threading
import time
import random
import anki_vector
from anki_vector.events import Events
from anki_vector.util import degrees, distance_mm, speed_mmps,  Angle
from anki_vector.behavior import MIN_HEAD_ANGLE, MAX_HEAD_ANGLE

interacted = False


def main():
    evt = threading.Event()

    def on_robot_observed_face(robot, event_type, event):
        global interacted
        print('event.name: ', event.name)
        if event.name == '':
            return

        touch_data = robot.touch.last_sensor_reading

        if touch_data is not None:
            being_touched = touch_data.is_being_touched

        if interacted:
            if not being_touched:
                return

        interacted = True

        print("Vector sees a face, event: ", event.face_id)

        robot.say_text("Hey")
        robot.say_text(event.name)
        robot.say_text("how are you feeling?")
        time.sleep(1)

        print("Expression: ", event.expression)

        if event.expression == 2:
            robot.behavior.set_eye_color(hue=0.17, saturation=1.00)
            time.sleep(1)
            robot.anim.play_animation('anim_pounce_success_02')
            robot.say_text("You are making me happy, so let's dance!")
            robot.behavior.set_head_angle(MAX_HEAD_ANGLE)
            # robot.behavior.drive_on_charger()

        elif event.expression == 3:
            robot.anim.play_animation('anim_pounce_success_02')
            robot.say_text("Oh my! What surprised you? Should I be scared?")
            robot.behavior.set_head_angle(MAX_HEAD_ANGLE)
            # robot.behavior.drive_on_charger()

        elif event.expression == 4:
            robot.say_text("Are you mad? Let me tell you a joke. Why did the chicken cross the road?")
            time.sleep(2)
            robot.behavior.set_eye_color(hue=0.0, saturation=0.6)
            robot.anim.play_animation('anim_eyepose_angry')
            time.sleep(1)
            robot.anim.play_animation('anim_keepaway_getout_frustrated_01')
            robot.say_text("To get to the other side.")
            robot.behavior.set_head_angle(MAX_HEAD_ANGLE)
            # robot.behavior.drive_on_charger()

        elif event.expression == 5:
            robot.anim.play_animation('anim_pounce_success_02')
            robot.say_text("Cheer up buttercup!")
            robot.behavior.set_head_angle(MIN_HEAD_ANGLE)
            time.sleep(1)
            robot.behavior.set_head_angle(MAX_HEAD_ANGLE)
            # robot.behavior.drive_on_charger()

        elif event.expression == 1:
            robot.anim.play_animation('anim_pounce_success_02')
            robot.say_text("Show some expression.")
            robot.behavior.set_head_angle(MAX_HEAD_ANGLE)
            # robot.behavior.drive_on_charger()

        else:
            print("unexpected expression", event.expression)
            robot.say.text("How are you feeling?")
            robot.anim.play_animation('anim_pounce_success_02')
            robot.behavior.set_head_angle(MAX_HEAD_ANGLE)
            # robot.behavior.drive_on_charger()

        # robot.anim.play_animation('anim_explorer_lookaround_01')
        # if not interacted:
        #     interacted = True
        #     # robot.say_text("I see a face!")
        #     evt.set()

    args = anki_vector.util.parse_command_args()

    with anki_vector.Robot(args.serial, enable_face_detection=True) as robot:
        robot.behavior.drive_off_charger()
        robot.vision.enable_face_detection(detect_faces=True, estimate_expression=True)

        # If necessary, move Vector's Head and Lift to make it easy to see his face
        robot.behavior.set_head_angle(degrees(45.0))
        robot.behavior.set_lift_height(0.0)

        on_robot_observed_face = functools.partial(on_robot_observed_face, robot)
        robot.events.subscribe(on_robot_observed_face, Events.robot_observed_face)

        print("------ waiting for face events, press ctrl+c to exit early ------")

        try:
            while True:
                if not evt.wait(timeout=5):
                    print("------ Do something ------")
                    angle = random.randint(0, 181)
                    dist = random.randint(0, 101)
                    speed = random.randint(0, 101)
                    rand = random.randint(0, 2)
                    if rand == 0:
                        robot.behavior.turn_in_place(degrees(angle))
                    elif rand == 1:
                        robot.behavior.drive_straight(distance_mm(dist), speed_mmps(speed), True)
                    robot.behavior.set_head_angle(MAX_HEAD_ANGLE)

        except KeyboardInterrupt:
            pass

    robot.events.unsubscribe(on_robot_observed_face, Events.robot_observed_face)


if __name__ == '__main__':
    main()