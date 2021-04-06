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

class Decision(Page):
    # form_model = "player"
    # form_fields = ['transcription']

    live_method = "live_sender"

    def vars_for_template(self):
        return {
            'task_number': self.player.task_number
        }


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