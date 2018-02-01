# An example of how to use AWS SNS with Python's boto
# By Stuart Myles @smyles
# http://aws.amazon.com/sns/
# https://github.com/boto/boto
#
# Inspired by parts of the Ruby SWF SNS tutorial http://docs.aws.amazon.com/amazonswf/latest/developerguide/swf-sns-tutorial-implementing-activities-poller.html
# And the Python SNS code in http://blog.coredumped.org/2010/04/amazon-announces-simple-notification.html and http://awsadvent.tumblr.com/post/37531769345/simple-notification-service-sns

import boto.sns as sns
import json

ACCESS = '<REPLACE_WITH_ACCESS_KEY_ID>'
SECRET = '<REPLACE_WITH_SECRET_ACCESS_KEY>'

class SNSTopicShell:

        def fail(self, reason):
                print(reason)

        def complete(self, result):
                print(result)

class SNSTopicCreator(SNSTopicShell):

        def _create_topic(self, sns_client):
            t = sns_client.create_topic('SNS_Sample_Topic')
            print(t)
            topic_arn = t['CreateTopicResponse']['CreateTopicResult']['TopicArn']
            # For an SMS notification, setting `DisplayName` is *required*. Note that
            # only the *first 10 characters* of the DisplayName will be shown on the
            # SMS message sent to the user, so choose your DisplayName wisely!
            if topic_arn:
                sns_client.set_topic_attributes(topic_arn, 'DisplayName', 'SNSSample')
            else:
                self.fail(reason=json.dumps({"reason", "Couldn't create SNS topic", "detail", "" }))
                return False, "Couldn't create SNS topic"
            return True, topic_arn
                              
        # Subscribe the user to an Amazon SNS topic
        def _subscribe_topic_activity(self, task):
            activity_data = { "topic_arn": None, "email": {"endpoint" : None, "SubscriptionArn" : None}, "sms": {"endpoint" : None, "SubscriptionArn" : None} }
            if task:
                input = json.loads(task)
                activity_data["email"]["endpoint"] = input["email"]
                activity_data["sms"]["endpoint"] = input["sms"]
            else:
                self.fail(reason=json.dumps({"reason", "Didn't receive any input!", "detail", "" }))
                return False, "Didn't receive any input!"

            sns_client = sns.SNSConnection(aws_access_key_id=ACCESS, aws_secret_access_key=SECRET)

            # Create the topic and get the ARN
            result, activity_data["topic_arn"] = self._create_topic(sns_client)
            if result:           
                    # Subscribe the user to the topic, using either or both endpoints.
                    for protocol in ["email", "sms"]:
                        ep = activity_data[protocol]["endpoint"]
                        if (ep):
                            print("About to subscribe protocol: " + protocol + " ep: " + ep)
                            response = sns_client.subscribe(activity_data["topic_arn"], protocol, ep)
                            print(response)
                            activity_data[protocol]["SubscriptionArn"] = response['SubscribeResponse']['SubscribeResult']["SubscriptionArn"]
                    # If at least one subscription arn is set, consider this a success.
                    if (activity_data["email"]["SubscriptionArn"] != None) or (activity_data["sms"]["SubscriptionArn"] != None):
                        self.complete(result=json.dumps(activity_data))
                        return True, json.dumps(activity_data)
                    else:
                        self.fail(reason=json.dumps({ "reason" : "Couldn't subscribe to SNS topic", "detail" : "" }))
                        return False, "Couldn't subscribe to SNS topic"
            else:
                return False, "Couldn't create SNS topic"


class SNSTopicWaiter(SNSTopicShell):

        # Wait for the user to confirm the subscription to the SNS topic
        def _wait_for_confirmation_activity(self, task):
            if task:
                subscription_data = json.loads(task)
            else:
                self.fail(reason=json.dumps({"reason", "Didn't receive any input!", "detail", "" }))
                return

            sns_client = sns.SNSConnection(aws_access_key_id=ACCESS, aws_secret_access_key=SECRET)
            topic = sns_client.get_topic_attributes(subscription_data["topic_arn"])

            if topic:
                subscription_confirmed = False
            else:
                self.fail(result=json.dumps({ "reason" : "Couldn't get SWF topic ARN", "detail" : "Topic ARN: %s" % subscription_data["topic_arn"] }))
                return

            # Loop through all of the subscriptions to this topic until we get some indication that a subscription was confirmed.
            while not subscription_confirmed:
                for sub in sns_client.get_all_subscriptions_by_topic(subscription_data["topic_arn"])["ListSubscriptionsByTopicResponse"]["ListSubscriptionsByTopicResult"]["Subscriptions"]:
                    if subscription_data[sub["Protocol"]]["endpoint"] == sub["Endpoint"]:
                        # this is one of the endpoints we're interested in. Is it subscribed?
                        if sub["SubscriptionArn"] != 'PendingConfirmation':
                            subscription_data[sub["Protocol"]]["subscription_arn"] = sub["SubscriptionArn"]
                            subscription_confirmed = True

            self.complete(result=json.dumps(subscription_data))
            return True, json.dumps(subscription_data)
            
class SNSTopicConfirmer(SNSTopicShell):

        # Send the user a confirmation of the successful topic subscription, using the topic that the user subscribed to and the endpoint that the user confirmed the subscription with
        def _send_result_activity(self, task):
            if task:
                subscription_data = json.loads(task)
            else:
                self.fail(reason=json.dumps({"reason", "Didn't receive any input!", "detail", "" }))
                return
            
            sns_client = sns.SNSConnection(aws_access_key_id=ACCESS, aws_secret_access_key=SECRET)
            results = "Thanks, you've successfully confirmed registration, and your workflow is complete!"
            # send the message via SNS

            sns_client.publish(topic=subscription_data["topic_arn"], message=results)
            self.complete(result=results)
            return True
                
if __name__ == '__main__':
    st = SNSTopicCreator()
    testtaskjs = json.dumps({ "email" : "<REPLACE_WITH_EMAIL_ADDRESS>", "sms" : "<REPLACE_WITH_SMS_ENABLED_PHONE_NUMBER>"})
    result, subscription_data = st._subscribe_topic_activity(testtaskjs)

    if result:
            sw = SNSTopicWaiter()
            result, subscription_data = sw._wait_for_confirmation_activity(subscription_data)
            if result:
                    sc = SNSTopicConfirmer()
                    if sc._send_result_activity(subscription_data):
                            print("It worked!")
                    else:
                            print("Confirmation failed...")
            else:
                    print("Waiting failed...")
    else:
            print("Creation failed...")


