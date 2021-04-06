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

from .text_to_png import writeText
from django.utils.translation import gettext as _
from base64 import b64encode
from os import remove
from os.path import exists

doc = """
This is a Lines Queueing project
"""

class Constants(BaseConstants):
    name_in_url = 'random_number_game'
    players_per_group = 4
    num_rounds = 4 # 1 round of repeated tasks per stage (practice + normal stages)
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

        if self.round_number == 2: # stage 1
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

            for group in self.get_groups():
                print(f"DEBUG: assigning stage to group {group}")
                group.stage =  2
                print(f"DEBUG: group stage = {group.stage}")

        
        # keeping the same grouping for the rest of rounds
        round_counter =  3
        
        for subsession in self.in_rounds(3, Constants.num_rounds): # for stage 2 and 3
            subsession.group_like_round(2) # group like stage 1

            print(f"DEBUG: assigning stage for round {round_counter}")
            print(f"DEBUG: subsession {subsession}")
            # assigning the stage for newly created groups
            for group in subsession.get_groups():
                print(f"DEBUG: group {group}")
                print(f"DEBUG: group stage (pre) = {group.stage}")
                group.stage = round_counter - 1
                print(f"DEBUG: group stage (post) = {group.stage}")
            round_counter += 1
                

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
            p.task_number_assign()

        # setting practice and 1st stage for groups created by default
        print("DEBUG: executing stage assignment")
        for group in self.get_groups():
            print(f"DEBUG: self.round_number = {self.round_number}")
            group.stage = self.round_number - 1


class Group(BaseGroup):
   
    stage = models.IntegerField()
    # best_score_stage_2 = models.IntegerField() # highest number of correct answers per group in S2

    def set_payoffs_s1_s2(self):
        """
        Sets the payoffs for each player in a group for
        stages 1 and 2

        Input: None
        Output: None
        """

        print("DEBUG: Executing set payoffs")
        print(f"DEBUG: stage = {self.stage}")
        if self.stage == 1:
            for player_in_group in self.get_players():
                player_in_group.payoff_stage_1 = player_in_group._correct_answers * 1500

        elif self.stage == 2:
            best_players_per_player = {} # dict of lists of best players for every player without considering themselves
            # self.best_score_stage_2 = 0 # Int, placeholder for best score
            
            # evaluating who is the best player
            for player_in_group in self.get_players():
                print("-------------------------------------------------")
                print(f"DEBUG: player {player_in_group.id_in_group} correct answers = {player_in_group._correct_answers}")
                # capturing the other players in his group
                for other_player in player_in_group.get_others_in_group():
                    print(f"DEBUG: getting player {other_player.id_in_group}")
                    print(f"DEBUG: player {other_player.id_in_group} score = {other_player._correct_answers}")
                    print(f"DEBUG: current player other's best score = {player_in_group.others_best_score_stage_2}")
                    # getting the best score of the other players in group
                    if player_in_group.others_best_score_stage_2 <= other_player._correct_answers:
                        # updating the best score
                        best_player = other_player
                        player_in_group.others_best_score_stage_2 = best_player._correct_answers
                print(f"DEBUG: best player correct answers = {player_in_group.others_best_score_stage_2}")
            
                # evaluating if more than one player obtained the best score
                best_players_per_player[f"best_for_p{player_in_group.id_in_group}"] = []
                # storing the best players per player
                for other_player in player_in_group.get_others_in_group():
                    # append if other player's score == best score in group
                    print(f"DEBUG: checking best players")
                    print(f"DEBUG: getting player {other_player.id_in_group}")
                    print(f"DEBUG: player {other_player.id_in_group} score = {other_player._correct_answers}")
                    if other_player._correct_answers == player_in_group.others_best_score_stage_2: 
                        best_players_per_player[f"best_for_p{player_in_group.id_in_group}"].append(other_player.id_in_group)
                print(f"DEBUG: dict of best players = {best_players_per_player}")
                
                # determining who won if more than 1 obtained the best score    
                best_players = best_players_per_player[f"best_for_p{player_in_group.id_in_group}"]
    
                best_other_player = None

                if len(best_players) > 1:
                    random.SystemRandom().shuffle(best_players) # randomizing the order for picking the winner at random
                
                # tracking the other best player with ids
                for player in self.get_players():
                    # if id in group of player matches the first best player, it is the best
                    if player.id_in_group == best_players[0]:
                        best_other_player = player
                
                # checking if player is winner
                if player_in_group.stage_2_winner == None:
                    # when player is absolute winner
                    if player_in_group._correct_answers > best_other_player._correct_answers: 
                        player_in_group.stage_2_winner = True
                        player_in_group.payoff_stage_2 = player_in_group._correct_answers * 6000
                        
                        # setting results for rest in round
                        for other_player in player_in_group.get_others_in_group():
                            other_player.stage_2_winner = False
                            other_player.stage_2_winner = 0

                    # if tie, choose at random
                    elif player_in_group._correct_answers == best_other_player._correct_answers:
                        win_prob = random.SystemRandom().randrange(1,101) # randrange is exclusive
                        if win_prob <= 50:
                            # setting results for player
                            player_in_group.stage_2_winner = False
                            player_in_group.payoff_stage_2 = 0
                            
                            # setting results for best player
                            best_other_player.stage_2_winner = True
                            best_other_player.payoff_stage_2 = best_other_player._correct_answers * 6000

                            # setting results for rest in round
                            for other_player in player_in_group.get_others_in_group():
                                if other_player != best_other_player:
                                    other_player.stage_2_winner = False
                                    other_player.stage_2_winner = 0

                        else:
                            player_in_group.stage_2_winner = True
                            player_in_group.payoff_stage_2 = player_in_group._correct_answers * 6000

                            # setting results for losers in round
                            for other_player in player_in_group.get_others_in_group():
                                other_player.stage_2_winner = False
                                other_player.stage_2_winner = 0

                    else:
                        player_in_group.stage_2_winner = False
                        player_in_group.payoff_stage_2 = 0

                        # setting results for best player
                        best_other_player.stage_2_winner = True
                        best_other_player.payoff_stage_2 = best_other_player._correct_answers * 6000

                        # setting results for rest in round
                        for other_player in player_in_group.get_others_in_group():
                            if other_player != best_other_player:
                                other_player.stage_2_winner = False
                                other_player.stage_2_winner = 0
                    
                    # storing the others best score in stage 2        
                    player_in_group.others_best_score_stage_2 = best_other_player._correct_answers

        else:
            print(f"DEBUG: Stage undefined value = {self.stage}")


class Player(BasePlayer):
    silo_num = models.IntegerField()
    task_number = models.StringField()
    task_number_path = models.StringField() # path for img
    encoded_image = models.LongStringField() # image encoded in base64
    task_number_command = models.StringField() # command for displaying task_number image file
    stage_round_number = models.IntegerField(initial=1)
    transcription = models.StringField()
    answer_is_correct = models.IntegerField()
    _correct_answers = models.IntegerField(initial=0)
    _gender_group_id = models.IntegerField()
    # benchmark_stage_2 = models.IntegerField() # stores the best stage 2 score for individual comparisons 
    stage_2_winner = models.BooleanField() # True if player wins, False if not
    payoff_stage_1 = models.CurrencyField()
    payoff_stage_2 = models.CurrencyField()
    payoff_stage_3 = models.CurrencyField()
    others_best_score_stage_2 = models.IntegerField(initial=0) # max correct answers for other players in player group (S2)

    _gender =  models.StringField(
        choices=[
            [_('Male'), 'Эрэгтэй'],
            [_('Female'), 'Эмэгтэй'],
        ],
        widget=widgets.RadioSelect,
        label='Таны Хүйс (эр/эм)?'
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

    def task_number_assign(self):
        self.task_number = self.task_number_method()

    def live_sender(self, data):
        """
        This live method is in charge of:

        - Sending the respective image to the decision page
        - Telling the decision page if player on practice stage
        - Checking if the transcription submitted is correct
        - Storing the total number of correct answers and images displayed
        - Erasing the image displayed at beginning of the round

        Input:
        - transcription (string)
        Output:
        - current stage round (Int), number of practice rounds (Int), encoded image (bs64), 
        player in practice stage (Boolean)
        """
        
        # logging received data
        print("received data", data)

        return_data = {} # dict with data to be used in live Decision page
        return_data["practice_rounds"] = Constants.num_rounds_practice
        self.stage_round_number = int(data["stage_round_number"]) # updating the round number each time this func executed

        ######### checking if transcription is correct and storing the total number of correct answers
        print(f"DEBUG: task_number = {self.task_number}")
        print(f"DEBUG: transcription = {data['transcription']}")
        if str(self.task_number) == data["transcription"]:
            self._correct_answers += 1

        ######### generating the images
        self.task_number = self.task_number_method()
        id_in_subsession = self.id_in_subsession
        
        # name of random number image file
        task_number_path = "random_number_game/" + \
                            f"task_number_player_{id_in_subsession}_{self.stage_round_number}"
        print("current task_number_path", task_number_path)

        # creating the img file
        writeText(self.task_number, f'random_number_game/static/{task_number_path}.png')
        
        # encoding the image that will be displayed in base64
        with open("random_number_game/static/" + task_number_path + ".png", "rb") as image_file:
            encoded_image = b64encode(image_file.read()).decode('utf-8')

        # sending the image to the player
        return_data["image"] = encoded_image

        ######### checking whether player in practice stage
        if self.round_number == 1: # 1st round = practice round
            return_data["practice_stage"] = True
        else:
            return_data["practice_stage"] = False
        
        ######### erasing the image displayed at beginning of the round
        print("stage_round_number: ", self.stage_round_number)
        if self.stage_round_number > 1:
            previous_round = self.stage_round_number - 1
            previous_task_number_path = "random_number_game/" + \
                            f"task_number_player_{id_in_subsession}_{previous_round}"
            file_to_erase = "random_number_game/static/" + previous_task_number_path + ".png"
            print(f"DEBUG: file_to_erase = {file_to_erase}")
            if exists(file_to_erase):
                remove(file_to_erase)
            else:
                print(f"Can not delete the file {file_to_erase} as it doesn't exists")

        ######### sending everything to the players in the live page
        print("practice_rounds", return_data["practice_rounds"])
        print("practice_stage", return_data["practice_stage"])
        return {0: return_data}


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
        # choice of last stage
        print(f"DEBUG: _choice = {self.in_round(4)._choice}")
        if self.in_round(4)._choice == 1: 
            print("DEBUG: paying in stage 3 according to stage 1")
            self.payoff_stage_3 = self._correct_answers * 1500
        # if stage 2 chosen
        elif self.in_round(4)._choice == 2: 
            print("DEBUG: paying in stage 3 according to stage 2")
            if self.in_round(Constants.num_rounds)._correct_answers \
                > self.in_round(3).others_best_score_stage_2:
                self.payoff_stage_3 = self._correct_answers * 6000
            else:
                self.payoff_stage_3 = 0

        if self.round_number == Constants.num_rounds:
            # choosing at random the player's final payoff from the stage payoffs
            list_of_payoffs = [[1, self.in_round(2).payoff_stage_1],
                               [2, self.in_round(3).payoff_stage_2],
                               [3, self.in_round(4).payoff_stage_3]]
            print(f"DEBUG: list of payoffs = {list_of_payoffs}")
            random.SystemRandom().shuffle(list_of_payoffs)
            print(f"DEBUG: list of payoffs shuffled = {list_of_payoffs}")
            self.payment_stage = list_of_payoffs[0][0]
            self.payoff = list_of_payoffs[0][1]
            print(f"DEBUG: final payoff = {self.payoff}")
                          