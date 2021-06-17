from typing import List
from pyrep.objects.object import Object
from pyrep.objects.shape import Shape
from pyrep.objects.proximity_sensor import ProximitySensor
from pyrep.objects.force_sensor import ForceSensor


class SuctionCup(Shape):
    """Represents all suction cups.
    """

    def __init__(self, count: int, name: str, base_name: str = None):
        suffix = '' if count == 0 else '#%d' % (count - 1)
        super().__init__(name + suffix if base_name is None else base_name + suffix)
        self._proximity_sensor = ProximitySensor('%s_sensor%s' % (name, suffix))
        self._attach_point = ProximitySensor('%s_sensor%s' % (name, suffix))
        self._old_parents: List[Object] = []
        self._grasped_objects: List[Object] = []
        self.joints = [0.0]

    def grasp(self, obj: Object) -> bool:
        """Attach the object to the suction cup if it is detected.

        Note: The does not move the object up to the suction cup. Therefore, the
        proximity sensor should have a short range in order for the suction
        grasp to look realistic.

        :param obj: The object to grasp if detected.
        :return: True if the object was detected/grasped.
        """
        detected = self._proximity_sensor.is_detected(obj)
        # Check if detected and that we are not already grasping it.
        if detected and obj not in self._grasped_objects:
            self._grasped_objects.append(obj)
            self._old_parents.append(obj.get_parent())  # type: ignore
            obj.set_parent(self._attach_point, keep_in_place=True)
            obj.set_dynamic(False)
            obj.set_respondable(False)
            self.joints = [1.0]
        return detected

    def release(self) -> None:
        """Release any objects that have been sucked.

        Note: The does not actuate the gripper, but instead simply detaches any
        grasped objects.
        """
        for grasped_obj, old_parent in zip(
                self._grasped_objects, self._old_parents):
            # Check if the object still exists
            if grasped_obj.still_exists():
                grasped_obj.set_parent(old_parent, keep_in_place=True)
                grasped_obj.set_dynamic(True)
                grasped_obj.set_respondable(True)
        self._grasped_objects = []
        self._old_parents = []
        self.joints = [0.0]

    def get_grasped_objects(self) -> List[Object]:
        """Gets the objects that are currently in the suction cup.

        :return: A list of grasped objects.
        """
        return self._grasped_objects

    def get_joint_positions(self) -> List[float]:
        """If there are attached object(s), return [1.0], otherwise return [0.0]
        """
        return self.joints

    def set_joint_positions(self, positions: List[float],
                            disable_dynamics: bool = False) -> None:
        """Currently always return None
        """
        return None

    def set_joint_target_velocities(self, velocities: List[float]) -> None:
        """Currently always return None
        """
        return None

    def get_open_amount(self) -> List[float]:
        """Gets the gripper open state. 1 means open, whilst 0 means closed.

        :return: A list of floats between 0 and 1 representing the gripper open
            state for each joint. 1 means open, whilst 0 means closed.
        """
        return self.joints

    def actuate(self, amount: float, velocity: float) -> bool:
        return True
        # if amount > 0.5:  # open
        #     self.release()
        #     return True
        # else:  # close
        #     return True

    def get_touch_sensor_forces(self) -> List[List[float]]:
        """Currently alwasy 0
        """
        return [[0.0, 0.0, 0.0]]
