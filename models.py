from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import csv
import random
import math
import otree.common
import time
import datetime
from django.utils.translation import gettext as _

doc = """
This is a Lines Queueing project
"""


class Constants(BaseConstants):
    name_in_url = 'random_number_game'
    players_per_group = 4
    num_rounds = 122 # 50 rounds per stage to make the respective page repeat itself 50 times + 2 rounds of practice
    # num_rounds = 8 # DEBUG num_rounds (stage rounds + practice rounds)
    num_rounds_practice = 2
    # timeout_practice = 20 # DEBUG timeout
    timeout_practice = 60
    # timeout_stage = 25 # DEBUG timeout
    timeout_stage = 3*60



class Subsession(BaseSubsession):

    def group_assignment(self):
        """
        Sets the group matrix for stage 2

        Input: None
        Output: None
        """

        if self.round_number == round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
            + Constants.num_rounds_practice + 1:
            group_matrix = self.get_group_matrix()
            female_players = [] # list of male player ids
            male_players = [] # list of female player ids
            new_id_matrix = [] # list of lists for ids of new group members
            print(f"DEBUG: Group matrix = {group_matrix}")
            for group in group_matrix:
                for player in group:
                    if player.in_round(1)._gender == 'Male':
                        male_players.append(player.id_in_subsession)
                    elif player.in_round(1)._gender == 'Female':
                        female_players.append(player.id_in_subsession)
                    else:
                        print(f"DEBUG: Invalid player gender = {player._gender}")
            
            # randomizing the order of the (fe)male players
            print(f"DEBUG: female_players = {female_players}")
            print(f"DEBUG: male_players = {male_players}")
            random.SystemRandom().shuffle(female_players)
            random.SystemRandom().shuffle(male_players)
            print(f"DEBUG: female_players shuffled = {female_players}")
            print(f"DEBUG: male_players shuffled = {male_players}")

            # setting up the new group matrix
            for group_number in range(0, len(group_matrix)):
                initial_index = (group_number)*2
                final_index = (group_number+1)*2
                print(f"DEBUG: current indexes = ({initial_index}, {final_index})")
                new_id_matrix.append(male_players[initial_index:final_index] + \
                                    female_players[initial_index:final_index])
                print(f"DEBUG: new_id_matrix = {new_id_matrix}")
            self.set_group_matrix(new_id_matrix)
            print(f"DEBUG: new group matrix = {self.get_group_matrix()}") 
        
        # keeping the same grouping for the rest of rounds
        for subsession in self.in_rounds(round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
            + Constants.num_rounds_practice + 2, Constants.num_rounds):
            subsession.group_like_round(round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
            + Constants.num_rounds_practice + 1)

    def creating_session(self):
        print(f"DEBUG: Executing creating session for round {self.round_number}")
        all_players = self.get_players()
        print(f"DEBUG: List of all players = {all_players}")
        for p in all_players:
            print(f"DEBUG: Player's id in subsession = {p.id_in_subsession}")
            if p.id_in_subsession <= round(len(all_players)/2):
                p._gender = "Male"
            else:
                p._gender = "Female"
            print(f"DEBUG: Player's gender = {p._gender}")


class Group(BaseGroup):
   
    stage = models.IntegerField()
    best_score_stage_2 = models.IntegerField() # highest number of correct answers per group in S2

    def set_payoffs(self):
        """
        Sets the payoffs for each player in a group

        Input: None
        Output: None
        """

        print("DEBUG: Executing set payoffs")
        print(f"DEBUG: stage = {self.stage}")
        if self.stage == 1:
            for player_in_group in self.get_players():
                player_in_group.payoff_stage_1 = player_in_group._correct_answers * 1500

        elif self.stage == 2:
            best_player = None # Player Object, placeholder for best player
            best_players = [] # List of ids in group, placeholder for best players (with same score)
            self.best_score_stage_2 = 0 # Int, placeholder for best score
            
            # evaluating who is the best player
            for player_in_group in self.get_players():
                print(f"DEBUG: player correct answers = {player_in_group._correct_answers}")
                if self.best_score_stage_2 <=  player_in_group._correct_answers:
                    best_player = player_in_group
                    self.best_score_stage_2 = best_player._correct_answers
            print(f"DEBUG: best player = {best_player}")
            print(f"DEBUG: best player correct answers = {best_player._correct_answers}")
            
            # evaluating if more than one player obtained the best score
            for player_in_group in self.get_players():
                if self.best_score_stage_2 ==  player_in_group._correct_answers:
                    best_players.append(player_in_group.id_in_group)
            print(f"DEBUG: list of best players = {best_players}")

            # declaring who won if more than 1 obtained the best score
            if len(best_players) > 1:
                random.SystemRandom().shuffle(best_players) # randomizing the order
                for player_in_group in self.get_players():
                    if player_in_group.id_in_group == best_players[0]: # picking the winner at random
                        player_in_group.stage_2_winner = True
                        player_in_group.payoff_stage_2 = player_in_group._correct_answers * 6000
                    else:
                        player_in_group.stage_2_winner = False
                        player_in_group.payoff_stage_2 = 0

            # declaring who won if only 1 player got best score
            else:
                best_player.stage_2_winner = True
                for player_in_group in self.get_players():
                    if player_in_group != best_player:
                        player_in_group.stage_2_winner = False
                        player_in_group.payoff_stage_2 = 0
                    else:
                        player_in_group.payoff_stage_2 = player_in_group._correct_answers * 6000

            # storing the best stage 2 score in each player obj
            for player_in_group in self.get_players():
                player_in_group.benchmark_stage_2 = self.best_score_stage_2

        else:
            print(f"DEBUG: Stage undefined value = {self.stage}")


class Player(BasePlayer):
    silo_num = models.IntegerField()
    task_number = models.StringField()
    task_number_path = models.StringField() # path for img
    encoded_image = models.LongStringField() # image encoded in base64
    task_number_command = models.StringField() # command for displaying task_number image file
    transcription = models.StringField()
    answer_is_correct = models.IntegerField()
    _correct_answers = models.IntegerField(initial=0)
    _gender_group_id = models.IntegerField()
    benchmark_stage_2 = models.IntegerField() # stores the best stage 2 score for individual comparisons 
    stage_2_winner = models.BooleanField() # True if player wins, False if not
    payoff_stage_1 = models.CurrencyField()
    payoff_stage_2 = models.CurrencyField()
    payoff_stage_3 = models.CurrencyField()

    _gender =  models.StringField(
        choices=[
            [_('Male'), 'Эрэгтэй'],
            [_('Female'), 'Эмэгтэй'],
        ],
        widget=widgets.RadioSelect,
        label=''
    )
    _choice =  models.IntegerField(
        choices=[
            1,
            2
        ],
        widget=widgets.RadioSelect,
        label=_('Асуулт: Ямар төлбөрийн системийг сонгох вэ?')
    ) # 1 is Stage 1 and 2 is Stage 2

    payment_stage = models.IntegerField()

    #Survey Fields
    # Gender is already recorded
    _age =  models.IntegerField(
        label=_('Та хэдэн настай вэ?')
    )
    # Birth Place
    _birth_place = models.StringField(
        label=_('Таны төрсөн аймаг, хот юу вэ?')
    )
    #3. School Name (I have a list of schools and other option in Mongolian)
    _school = models.StringField(
        label=_('Танай сургуулийнг нэр юу вэ?')
    )
    #4. Year of School (1-6, other=type)
    _year_of_school = models.IntegerField(
        label=_('Хэддүгээр курс вэ?')
    )
    #5 . Field of Study (I have a list of majors and other option to type)
    _major = models.StringField(
        label=_('Та ямар чиглэлээр сурдаг вэ?')
    )
    #6. How many brothers do you have?
    _brothers = models.IntegerField(
        label=_('Та хэдэн ах болон эрэгтэй дүүтэй вэ?')
    )
    #7 . How many sisters do you have?
    _sisters = models.IntegerField(
        label=_('Та хэдэн эгч болон эмэгтэй дүүтэй вэ?')
    )
    #8. Explain briefly the reason behind your choice in Stage 3 (short answer)
    _stage_3_reasoning =  models.StringField(
        label=_('3-р шатны сонголтынхоо шалтгааныг товч тайлбарла (богино хариулт)')
    )

    def set_correct_answer(self, transcription):
        """
        Verifies that the number inputted is correct and adds 
        increases the count of correct answers if that's the
        case

        Input: transcripted number (integer)
        Output: None
        """
        # determining if answer is correct
        if transcription == self.task_number:
            self.answer_is_correct = 1
        else:
            self.answer_is_correct = 0

        # storing the number of correct answers
        print(f"DEBUG: current round = {self.round_number}")
        if self.round_number >= 1 and self.round_number <= Constants.num_rounds_practice:
            print(f"DEBUG: correct answers s0 = {self.participant.vars['correct_answers_s0']}")
            print(f"DEBUG: answer is correct = {self.answer_is_correct}")
            self.participant.vars['correct_answers_s0'] += self.answer_is_correct  
            self._correct_answers = self.participant.vars['correct_answers_s0']
            print(f"DEBUG: correct answers s0 += = {self.participant.vars['correct_answers_s0']}")

        elif self.round_number >= 1 + Constants.num_rounds_practice and \
            self.round_number <= round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
            + Constants.num_rounds_practice:
            
            print(f"DEBUG: correct answers s1 = {self.participant.vars['correct_answers_s1']}")
            print(f"DEBUG: answer is correct = {self.answer_is_correct}")
            self.participant.vars['correct_answers_s1'] += self.answer_is_correct  
            self._correct_answers = self.participant.vars['correct_answers_s1']
            print(f"DEBUG: correct answers s1 += = {self.participant.vars['correct_answers_s1']}")

        elif self.round_number > round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
            + Constants.num_rounds_practice and \
            self.round_number <= round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
            + Constants.num_rounds_practice:

            self.participant.vars['correct_answers_s2'] += self.answer_is_correct  
            self._correct_answers = self.participant.vars['correct_answers_s2']
        else:
            self.participant.vars['correct_answers_s3'] += self.answer_is_correct
            self._correct_answers = self.participant.vars['correct_answers_s3']

    def task_number_method(self):
        """
        Creates a random 9-digit number as a string for transcription 
        with unique digits

        Input: None
        Output: task number (string)
        """

        random_number = ""
        one_to_nine = [num for num in range(1, 10)] # list with numbers from 1 to 9

        random.SystemRandom().shuffle(one_to_nine) # shuffling the order of its items

        # turning the list into a string
        for num in one_to_nine:
            random_number += str(num)

        return random_number

    def set_final_payoff(self):
        """
        Sets the payoff of a player who finishes stage 3

        Input: None
        Output: None
        """
        # for stage 3:
        # paying the player according to his stage system choice
        # if stage 1 chosen
        print(f"DEBUG: _choice = {self.in_round(round(2*Constants.num_rounds/3) + 1)._choice}")
        if self.in_round(round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
               + Constants.num_rounds_practice + 1)._choice == 1:
            print("DEBUG: paying in stage 3 according to stage 1")
            self.payoff_stage_3 = self._correct_answers * 1500
        # if stage 2 chosen
        elif self.in_round(round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
               + Constants.num_rounds_practice + 1)._choice == 2: 
            print("DEBUG: paying in stage 3 according to stage 2")
            if self.in_round(Constants.num_rounds)._correct_answers \
                > self.in_round(round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
               + Constants.num_rounds_practice).benchmark_stage_2:
                self.payoff_stage_3 = self._correct_answers * 6000
            else:
                self.payoff_stage_3 = 0

        if self.round_number == Constants.num_rounds:
            # choosing at random the player's final payoff from the stage payoffs
            list_of_payoffs = [[1, self.in_round(round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
                               + Constants.num_rounds_practice).payoff_stage_1],
                               [2, self.in_round(round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
                               + Constants.num_rounds_practice).payoff_stage_2],
                               [3, self.in_round(Constants.num_rounds).payoff_stage_3]]
            print(f"DEBUG: list of payoffs = {list_of_payoffs}")
            random.SystemRandom().shuffle(list_of_payoffs)
            print(f"DEBUG: list of payoffs shuffled = {list_of_payoffs}")
            self.payment_stage = list_of_payoffs[0][0]
            self.payoff = list_of_payoffs[0][1]
            print(f"DEBUG: final payoff = {self.payoff}")
                          