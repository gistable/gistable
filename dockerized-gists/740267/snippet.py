#!/usr/bin/env python

### Requires latest boto (cuz I checked in code to boto a moment ago)

import uuid
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import Question, QuestionForm, QuestionContent
from boto.mturk.question import AnswerSpecification, FreeTextAnswer
from boto.mturk.question import Overview
#from boto.mturk.qualification import Qualifications # these exist!
#from boto.mturk.qualification import Requirement    # these too


#####################
# Connect to Amazon #
#####################

aws_access_key_id = ''
aws_secret_access_key = ''
aws_host = 'mechanicalturk.sandbox.amazonaws.com'
#aws_host = 'mechanicalturk.amazonaws.com'

mtc = MTurkConnection(aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      host=aws_host)


###################################
# Start building the hit template #
###################################


# Overview design
#
# The overview is used for question oriented text and can be interwoven with
# QuestionContent's inside a QuestionForm.
#
# For this demo, I use only one Overview at the top of the QuestionForm and
# then use five QuestionContents below to host input boxes.

overview_title = 'List your top 5 fav things'
overview_content = """<![CDATA[
<p>Please list your top five favorite things in the box
below. It would help our research if you kept the names general. For example,
instead of saying \"playing shortstop\", please just say, \"baseball\".</p>

<p>Thanks, James and the boto crew</p>
]]>"""

overview = Overview()
overview.append_field('Title', overview_title)
overview.append_field('FormattedContent', overview_content)


# Question design
#
# Questions can each be designed uniquely. For this demo I only build enough
# of a QuestionContent to host an input box by using a FreeTextAnswer. There
# are multiple options for how a QuestionContent is constructed.
#
# I recommend reading: http://docs.amazonwebservices.com/AWSMechanicalTurkRequester/2007-06-21/ApiReference_QuestionFormDataStructureArticle.html
#
# Quickly, the available content types are: Title, Text, List, Binary,
#                                           Application, EmbeddedBinary,
#                                           FormattedContent

question_list = []
for i in xrange(5):
    qc = QuestionContent()
    qc.append_field('Text', "Fav #%s:" % i)
    fta = FreeTextAnswer()
    ansp = AnswerSpecification(fta)
    q = Question(identifier=str(uuid.uuid4()),
                 content=qc,
                 answer_spec=ansp)
    question_list.append(q)

    
# QuestionForm design
#
# A QuestionForm is a container for what the HIT task is shaped like. In this
# example, we build one like:
#
#     <QuestionForm>
#        <Overview></Overview>
#        <QuestionContent></QuestionContent>
#        ...,
#        <QuestionContent></QuestionContent>
#     </QuestionForm>

question_form_title=overview_title # reuse it
question_form_description='Help us by listing your five favorite things'
question_form_reward=0.2

qf = QuestionForm()
qf.append(overview)
for q in question_list:
    qf.append(q)


# Assignments is an interesting concept in the mechanical turk API. You can have
# multiple instances of a hit's design by assigning it multiple times.
#
# Many users, however, work through the web interface and seem to create many
# copies of the same HIT instead. Be mindful of the way assignments are used.
max_assignments = 1
    
# create funciton to make a hit using our arguments
make_demo_hit = lambda: mtc.create_hit(question=qf,
                                       max_assignments=max_assignments,
                                       title=question_form_title,
                                       description=question_form_description,
                                       reward=question_form_reward)

hit_set = make_demo_hit()
