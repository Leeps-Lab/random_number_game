import math
from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from datetime import timedelta
from operator import concat

from .text_to_png import writeText
from django.utils.html import format_html

from time import time
from os import remove
from base64 import b64encode

  
class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        print(f"DEBUG: treatment = {self.session.config['treatment']}")
        return {'treatment': self.session.config["treatment"]}
    
    def before_next_page(self):
        ##### creating first image of stage
        task_number = self.player.task_number
        id_in_subsession = self.player.id_in_subsession
        
        # name of random number image file
        task_number_path = "random_number_game/" + \
                            f"task_number_player_{id_in_subsession}_{1}"
        print("current task_number_path", task_number_path)

        # creating the img file
        writeText(task_number, f'random_number_game/static/{task_number_path}.png')


class GenderPage(Page):
    form_model = 'player'
    form_fields = ['_gender']

    def is_displayed(self):
        return self.round_number == 1


class ChoicePage(Page):   
    form_model = 'player'
    form_fields = ['_choice']

    def is_displayed(self):
        return self.round_number == 4 # displays on beginning of third stage
    
    def vars_for_template(self):
        print(f"DEBUG: treatment = {self.session.config['treatment']}")
        return {'treatment': self.session.config["treatment"]}


class Stage2WaitPage(WaitPage):
    """
    WaitPage for assigning each player to their respective
    2 men 2 women group for Stage 2
    """
    
    body_text = 'Waiting for all players to be ready'
    wait_for_all_groups = True
    after_all_players_arrive = 'group_assignment' # players will be assigned into groups of 2 men and 2 women

    def is_displayed(self):
        return self.round_number == 3 # displays on beginning of second stage


# class ProcessingPage(Page):
#     timeout_seconds = 0.5 #TODO: test if non-integer timeouts work

#     def before_next_page(self):
#         # creating the number images and storing their commands to display on page
#         player = self.player
#         player.task_number = self.player.task_number_method()
#         # name of random number image file
#         id_in_subsession = self.player.id_in_subsession
#         player.task_number_path = "random_number_game/" + \
#                             f"task_number_player_{id_in_subsession}_{self.round_number}"
#         # creating the img file
#         writeText(player.task_number, f'random_number_game/static/{player.task_number_path}.png')

#         # erasing file if no time remaining
#         #TODO: look for a ram efficient way to create and erase images
#         if self.round_number > 1:
#             remaining_time = self.participant.vars['expiry_time_s{self.group.stage}'] - time()
#             if remaining_time <= 0:
#                 file_to_erase = "random_number_game/static/" + self.player.task_number_path + ".png"
#                 print(f"DEBUG: file_to_erase = {file_to_erase}")
#                 remove(file_to_erase)

#                     # # updating the correct answers when no remaining time
#                     # self.player.set_correct_answer(self.player.transcription)

#     def vars_for_template(self):
#         if self.round_number > 1:
#             remaining_time = self.participant.vars['expiry_time_s{self.group.stage}'] - time()
#         else:
#             remaining_time = 10 # arbitrary value in order to make this code run
#         return {"remaining_time": remaining_time}

#     def is_displayed(self):
#         # avoid displaying the processing page if no remaining time
#         print(f"DEBUG: round = {self.round_number}")
#         print(f"DEBUG: conditional round 1 = {1 + Constants.num_rounds_practice}")
#         cond1 = self.round_number == 1 + Constants.num_rounds_practice
#         print(f"DEBUG: cond 1 = {cond1}")
#         cond2 = self.round_number == round((Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1
#         print(f"DEBUG: conditional round 2 = {round((Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1}")
#         print(f"DEBUG: cond 2 = {cond2}")
#         cond3 = round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1
#         print(f"DEBUG: conditional round 3 = {cond3}")
#         print(f"DEBUG: cond 3 = {self.round_number == round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1}")
        
#         if self.round_number == 1:
#             print(f"DEBUG: correct_answers_s{self.group.stage}")
#             self.participant.vars[f'correct_answers_s{self.group.stage}'] = 0 # setting up the corr answ counter
#             self.participant.vars['expiry_time_s{self.group.stage}'] = time() + Constants.timeout_practice
#             print(f"DEBUG: expiry_time_s{self.group.stage} = {self.participant.vars['expiry_time_s{self.group.stage}']}")

#         elif self.round_number == 1 + Constants.num_rounds_practice or \
#            self.round_number == round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
#            + Constants.num_rounds_practice + 1 or\
#            self.round_number == round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
#             + Constants.num_rounds_practice + 1:

#             print(f"DEBUG: correct_answers_s{self.group.stage}")
#             self.participant.vars[f'correct_answers_s{self.group.stage}'] = 0 # setting up the corr answ counter
#             self.participant.vars['expiry_time_s{self.group.stage}'] = time() + Constants.timeout_stage
#             print(f"DEBUG: expiry_time_s{self.group.stage} = {self.participant.vars['expiry_time_s{self.group.stage}']}")

#         if self.round_number > 1:
#             remaining_time = self.participant.vars['expiry_time_s{self.group.stage}'] - time()
#             if remaining_time <= 0:                
#                 # avoiding the display of this page if no time remaining
#                 return False
#             else:
#                 return True
#         else:
#             return True


class Decision(Page):
    # form_model = "player"
    # form_fields = ['transcription']

    live_method = "live_sender"

    def before_next_page(self):    
        ##### creating first image of stage
        task_number = self.player.task_number
        id_in_subsession = self.player.id_in_subsession
        
        # name of random number image file
        task_number_path = "random_number_game/" + \
                            f"task_number_player_{id_in_subsession}_{1}"
        print("current task_number_path", task_number_path)

        # creating the img file
        writeText(task_number, f'random_number_game/static/{task_number_path}.png')


    # def get_timeout_seconds(self):
    #     # getting expiry time
    #     if self.round_number == 1:
    #         expiry_time = Constants.timeout_practice
    #     else:
    #         expiry_time = Constants.timeout_stage

    #     return expiry_time # updating the time each time the page is displayed

    # def is_displayed(self):
    #     remaining_time = self.participant.vars['expiry_time_s{self.group.stage}'] - time()
    #     print(f"DEBUG: remaining time stage {self.group.stage} = {remaining_time}")
    #     return remaining_time > 0 # display only if there is time left

    # def before_next_page(self):
    #     # erasing file if still time on the clock, but round task finished
    #     file_to_erase = "random_number_game/static/" + self.player.task_number_path + ".png"
    #     print(f"DEBUG: file_to_erase = {file_to_erase}")
    #     remove(file_to_erase)
    #     self.player.set_correct_answer(self.player.transcription) # checking if the answer was correct

    def vars_for_template(self):
        id_in_subsession = self.player.id_in_subsession
        # encoding the image that will be displayed
        # name of random number image file
        task_number_path = "random_number_game/" + \
                            f"task_number_player_{id_in_subsession}_{1}"
        
        with open("random_number_game/static/" + task_number_path + ".png", "rb") as image_file:
            self.player.encoded_image = b64encode(image_file.read()).decode('utf-8')

        # using a var for template to display the encoded image
        return {"encoded_image": self.player.encoded_image}


class SettingAnswers(Page):
    """
    Page added only for processing the correct answers when the 
    player run out of time
    """
    timeout_seconds = 0

    def is_displayed(self):
        return self.participant.vars['expiry_time_s{self.group.stage}'] - time() < 0

    def before_next_page(self):
        self.player.set_correct_answer(self.player.transcription) # checking if the answer was correct


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_payoffs()

    def is_displayed(self):
        return self.round_number > 1 & self.round_number < 4 # stage 1 and 2


class FinalProcessingPage(Page):
    timeout_seconds = 0.5

    def before_next_page(self):
        self.player.set_final_payoff()

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


class Results(Page):

    def vars_for_template(self):
        return{
            'correct_answers': self.player._correct_answers
        }
        
class Survey(Page):   
    form_model = 'player'
    form_fields = ['_gender', '_age', '_birth_place', '_school', '_year_of_school', '_major', '_brothers' , '_sisters', '_stage_3_reasoning']

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

class Payment(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds
    
    def vars_for_template(self):
        payoff_1 = self.player.in_round(2).payoff_stage_1
        payoff_2 = self.player.in_round(3).payoff_stage_2
        payoff_3 = self.player.in_round(Constants.num_rounds).payoff_stage_3

        return {
            'payoff_1': payoff_1,
            'payoff_2': payoff_2,
            'payoff_3': payoff_3,
            'payment_stage': self.player.payment_stage,
            'payoff_plus_fee': self.participant.payoff_plus_participation_fee(),
            'treatment': self.session.config["treatment"]
        }

page_sequence = [
    Introduction,
#    GenderPage,
    ChoicePage,
    Stage2WaitPage,
    # ProcessingPage,
    Decision,
    # SettingAnswers,
    ResultsWaitPage,
    FinalProcessingPage,
    Results,
    Survey,
    Payment
]