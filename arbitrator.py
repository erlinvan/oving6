class Arbitrator():
    def __init__(self,behaviors):
        self.behaviors = behaviors
        self.halt_flag = False



    # getting the most valuable behavior
    def get_behavior(self):
        max_weighted_behavior = None
        max_weight = -1
        for behavior in self.behaviors:
            if behavior.halt_flag:
                self.halt_flag = True
                return behavior
            if behavior.weight > max_weight:
                max_weight = behavior.weight
                max_weighted_behavior = behavior

        return max_weighted_behavior




    # Regardless of the selection strategy, choose action should return a tuple
    # containing: 1. motor recommendations(one per motob) to move the robot,
    # and 2. a boolean indicating whether or not the run should be halted.
    def choose_action(self):
        behavior = self.get_behavior()
        motor_recommendation = behavior.motor_recommandations
        return (motor_recommendation, self.halt_flag)
