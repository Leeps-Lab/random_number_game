import math
from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from datetime import timedelta
from operator import concat

from django.utils.html import format_html

from PIL import Image, ImageDraw, ImageFont
from time import time
from os import remove
from base64 import b64encode

def writeText(text, fileName):
    """"
    This method generates the image version of an inputted text
    and saves it to fileName
    
    Input: text to be transcripted into the image, name of the output img file
    Output: None
    """

    image = Image.open('random_number_game/background.png')
    image = image.resize((250, 50))
    image.save('random_number_game/background.png')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('random_number_game/Roboto-Regular.ttf', size=19)
    imageChars = 100
    numLines = len(text) / imageChars
    numLines = math.ceil(numLines)
    lines = []

    for i in range(numLines):
        if(imageChars * (i + 1) < len(text)):
            lines.append(text[imageChars * i : imageChars * (i+1)])
        else:
            lines.append(text[imageChars * i : len(text)])

    for i in range(numLines):
        (x, y) = (10, 20 * i)
        message = lines[i]
        print("Message is: ", message)
        color = 'rgb(0, 0, 0)' # black color
        draw.text((x, y), message, fill=color, font=font)

    image.save(fileName) # stores the image on a specified folder


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
        return self.round_number == round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
               + Constants.num_rounds_practice + 1 # displays on beginning of third stage
    
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
        return self.round_number == round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
            + Constants.num_rounds_practice + 1 # displays on beginning of second stage


class ProcessingPage(Page):
    timeout_seconds = 0.5 #TODO: test if non-integer timeouts work

    def before_next_page(self):
        # creating the number images and storing their commands to display on page
        player = self.player
        player.task_number = self.player.task_number_method()
        # name of random number image file
        id_in_subsession = self.player.id_in_subsession
        player.task_number_path = "random_number_game/" + \
                            f"task_number_player_{id_in_subsession}_{self.round_number}"
        # creating the img file
        writeText(player.task_number, f'random_number_game/static/{player.task_number_path}.png')

        # assigning 2nd and 3rd stage
        # print("DEBUG: executing stage assignment")
        # if self.round_number >= 1 and self.round_number <= Constants.num_rounds_practice:
        #     print("DEBUG: executing practice stage assignment")
        #     self.group.stage = 0

        # elif self.round_number >= 1 + Constants.num_rounds_practice and \
        #     self.round_number <= round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
        #         + Constants.num_rounds_practice:
            
        #     print("DEBUG: executing stage 1 assignment")
        #     self.group.stage = 1
        
        # if self.round_number > round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
        #     + Constants.num_rounds_practice and \
        #     self.round_number <= round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
        #     + Constants.num_rounds_practice:    
        #     print("DEBUG: executing stage 2 assignment")
        #     self.group.stage = 2

        # elif self.round_number > round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
        #     + Constants.num_rounds_practice:
        #     print("DEBUG: executing stage 3 assignment")
        #     self.group.stage = 3

        # # timeout for multiple pages that restarts at beginning of practice stage
        # if self.round_number == 1:
        #     print("DEBUG: correct_answers practice stage")
        #     self.participant.vars[f'correct_answers_s{self.group.stage}'] = 0 # setting up the corr answ counter
        #     self.participant.vars['expiry_time'] = time() + Constants.timeout_practice

        # timeout for multiple pages that restarts at beginning of each stage
        # print(f"DEBUG: round = {self.round_number}")
        # print(f"DEBUG: conditional round 1 = {1 + Constants.num_rounds_practice}")
        # cond1 = self.round_number == 1 + Constants.num_rounds_practice
        # print(f"DEBUG: cond 1 = {cond1}")
        # cond2 = self.round_number == round((Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1
        # print(f"DEBUG: conditional round 2 = {round((Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1}")
        # print(f"DEBUG: cond 2 = {cond2}")
        # cond3 = round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1
        # print(f"DEBUG: conditional round 3 = {cond3}")
        # print(f"DEBUG: cond 3 = {self.round_number == round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1}")
        # if self.round_number == 1 or \
        #    self.round_number == 1 + Constants.num_rounds_practice or \
        #    self.round_number == round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
        #    + Constants.num_rounds_practice + 1 or\
        #    self.round_number == round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
        #     + Constants.num_rounds_practice + 1:

        #     print(f"DEBUG: correct_answers_s{self.group.stage}")
        #     self.participant.vars[f'correct_answers_s{self.group.stage}'] = 0 # setting up the corr answ counter
        #     self.participant.vars['expiry_time_s{self.group.stage}'] = time() + Constants.timeout_stage
        #     print(f"DEBUG: expiry_time_s{self.group.stage} = {self.participant.vars['expiry_time_s{self.group.stage}']}")

        # erasing file if no time remaining
        #TODO: look for a ram efficient way to create and erase images
        if self.round_number > 1:
            remaining_time = self.participant.vars['expiry_time_s{self.group.stage}'] - time()
            if remaining_time <= 0:
                file_to_erase = "random_number_game/static/" + self.player.task_number_path + ".png"
                print(f"DEBUG: file_to_erase = {file_to_erase}")
                remove(file_to_erase)

                    # # updating the correct answers when no remaining time
                    # self.player.set_correct_answer(self.player.transcription)

    def vars_for_template(self):
        if self.round_number > 1:
            remaining_time = self.participant.vars['expiry_time_s{self.group.stage}'] - time()
        else:
            remaining_time = 10 # arbitrary value in order to make this code run
        return {"remaining_time": remaining_time}

    def is_displayed(self):
        # avoid displaying the processing page if no remaining time
        print(f"DEBUG: round = {self.round_number}")
        print(f"DEBUG: conditional round 1 = {1 + Constants.num_rounds_practice}")
        cond1 = self.round_number == 1 + Constants.num_rounds_practice
        print(f"DEBUG: cond 1 = {cond1}")
        cond2 = self.round_number == round((Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1
        print(f"DEBUG: conditional round 2 = {round((Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1}")
        print(f"DEBUG: cond 2 = {cond2}")
        cond3 = round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1
        print(f"DEBUG: conditional round 3 = {cond3}")
        print(f"DEBUG: cond 3 = {self.round_number == round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) + Constants.num_rounds_practice + 1}")
        
        if self.round_number == 1:
            print(f"DEBUG: correct_answers_s{self.group.stage}")
            self.participant.vars[f'correct_answers_s{self.group.stage}'] = 0 # setting up the corr answ counter
            self.participant.vars['expiry_time_s{self.group.stage}'] = time() + Constants.timeout_practice
            print(f"DEBUG: expiry_time_s{self.group.stage} = {self.participant.vars['expiry_time_s{self.group.stage}']}")

        elif self.round_number == 1 + Constants.num_rounds_practice or \
           self.round_number == round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
           + Constants.num_rounds_practice + 1 or\
           self.round_number == round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
            + Constants.num_rounds_practice + 1:

            print(f"DEBUG: correct_answers_s{self.group.stage}")
            self.participant.vars[f'correct_answers_s{self.group.stage}'] = 0 # setting up the corr answ counter
            self.participant.vars['expiry_time_s{self.group.stage}'] = time() + Constants.timeout_stage
            print(f"DEBUG: expiry_time_s{self.group.stage} = {self.participant.vars['expiry_time_s{self.group.stage}']}")

        if self.round_number > 1:
            remaining_time = self.participant.vars['expiry_time_s{self.group.stage}'] - time()
            if remaining_time <= 0:                
                # avoiding the display of this page if no time remaining
                return False
            else:
                return True
        else:
            return True


class Decision(Page):
    form_model = "player"
    form_fields = ['transcription']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry_time_s{self.group.stage}'] - time() # updating the time each time the page is displayed

    def is_displayed(self):
        remaining_time = self.participant.vars['expiry_time_s{self.group.stage}'] - time()
        print(f"DEBUG: remaining time stage {self.group.stage} = {remaining_time}")
        return remaining_time > 0 # display only if there is time left

    def before_next_page(self):
        # erasing file if still time on the clock, but round task finished
        file_to_erase = "random_number_game/static/" + self.player.task_number_path + ".png"
        print(f"DEBUG: file_to_erase = {file_to_erase}")
        remove(file_to_erase)
        self.player.set_correct_answer(self.player.transcription) # checking if the answer was correct

    def vars_for_template(self):
        time_expired = (self.participant.vars['expiry_time_s{self.group.stage}'] - time() <= 0)
        print(f"DEBUG: time_expired = {time_expired}")
        
        # encoding the image that will be displayed
        with open("random_number_game/static/" + self.player.task_number_path + ".png", "rb") as image_file:
            self.player.encoded_image = b64encode(image_file.read()).decode('utf-8')

        # using a var for template to display the encoded image
        return {"encoded_image": self.player.encoded_image,
                "time_expired": time_expired}


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
        return self.round_number == round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
               + Constants.num_rounds_practice or \
               self.round_number == round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
               + Constants.num_rounds_practice 


class FinalProcessingPage(Page):
    timeout_seconds = 0.5

    def before_next_page(self):
        self.player.set_final_payoff()

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


class Results(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds_practice or \
               self.round_number == round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
               + Constants.num_rounds_practice or \
               self.round_number == round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
               + Constants.num_rounds_practice or \
               self.round_number == Constants.num_rounds    

    def vars_for_template(self):
        return{
            'correct_answers': self.player._correct_answers
        }
        
class Survey(Page):   
    form_model = 'player'
    form_fields = ['_age', '_birth_place', '_school', '_year_of_school', '_major', '_brothers' , '_sisters', '_stage_3_reasoning']

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

class Payment(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds
    
    def vars_for_template(self):
        payoff_1 = self.player.in_round(round((Constants.num_rounds - Constants.num_rounds_practice)/3) \
               + Constants.num_rounds_practice).payoff_stage_1
        payoff_2 = self.player.in_round(round(2*(Constants.num_rounds - Constants.num_rounds_practice)/3) \
               + Constants.num_rounds_practice).payoff_stage_2
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
    ProcessingPage,
    Decision,
    SettingAnswers,
    ResultsWaitPage,
    FinalProcessingPage,
    Results,
    Survey,
    Payment
]