#******************models.py**************************************************#
from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    question = models.TextField()
    
    def __unicode__(self):
        return self.question
    
class Answer(models.Model):
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=50)
    correct = models.BooleanField(default=False)
    
    def is_correct(self):
        return self.correct
    
    def __unicode__(self):
        return self.answer

class Guess(models.Model):
    submitted_by = models.ForeignKey(User)
    answer_given = models.ForeignKey(Answer)


#**********************views.py**********************************************#
from django.template import RequestContext
from django.shortcuts import render_to_response
from customform import CustomForm

def start_quiz(request):
    """
    """
    form = CustomForm()
    variables = RequestContext(request, {'form': form})
    print form.questions
    return render_to_response('quiz_page.html', variables)
    
def score(request):
    score = 0
    if request.POST:
        score = CustomForm(data=request.POST, user=request.user).get_score()
        print score
    variables = RequestContext(request, {'score':score})
    return render_to_response('result_page.html', variables)


#**************************customform.py******************************************#
import models
from django.utils.safestring import mark_safe
    
class CustomForm(object):
	""" Custom form containing multiple instances of 2 models
		presented as a single form.
	"""
    def __init__(self, data=None, user=None, num_of_questions=10):
#        self.generated_ids = ''
        self.user = user
        self.data = data
        self.num_of_questions = num_of_questions
        self.questions = models.Question.objects.none()
        self.answers = models.Answer.objects.none()
        
        if not self.data:
            # If data is empty then give a list of questions with options
            # There should actually be some shuffling of extracts from the
            # database here.....
            self.questions = models.Question.objects.all()[:self.num_of_questions]
            
    def __unicode__(self):
        return self.html()
                                
    def get_score(self):
        """ Check scores submitted and return number of correct answers """
        score = 0
        if self.data:
            id_list = []
			# I'm sure the following is buggy...
            for key in self.data:
                if key == u'csrfmiddlewaretoken':
                    continue
                id_list.append(int(key))
            self.answers = models.Answer.objects.in_bulk(id_list)
            for key in self.answers:
                new_guess = models.Guess.objects.create(submitted_by=self.user,
                                answer_given=self.answers[key])
                if self.answers[key].is_correct():
                    score += 1
        return score
                    
    def _html_output(self, row):
        """ Helper for outputing html() """
        output = []
        if row and self.questions:
            for q in self.questions:
                question = q.question
                question_id = q.id
#               self.generated_ids = self.generated_ids + ',' + unicode(question_id)
                answers = q.answer_set.all() #This saves all the Answer objects related to the Question instance
                choice1, choice2, choice3, choice4 = answers
                print choice1.id
                output.append(row % {'question_text': unicode(question),
                                     'choice1': unicode(choice1),
                                     'choice1_id': unicode(choice1.id),
                                     'choice2': unicode(choice2),
                                     'choice2_id': unicode(choice2.id),
                                     'choice3': unicode(choice3),
                                     'choice3_id': unicode(choice3.id),
                                     'choice4': unicode(choice4),
                                     'choice4_id': unicode(choice4.id),
                                     })
            return mark_safe(u'\n'.join(output))
        
    def html(self):
        """ Function to display form html """
        return self._html_output(
            row = u'<fieldset><p>%(question_text)s</p>\
                <input type="radio" name="%(choice1_id)s" value="%(choice1)s" />%(choice1)s\
                <input type="radio" name="%(choice2_id)s" value="%(choice2)s" />%(choice2)s\
                <input type="radio" name="%(choice3_id)s" value="%(choice3)s" />%(choice3)s\
                <input type="radio" name="%(choice4_id)s" value="%(choice4)s" />%(choice4)s\
                </fieldset>')
