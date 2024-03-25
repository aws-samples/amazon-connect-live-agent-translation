# Building a multilingual contact center for Medicaid agencies on AWS

One of the biggest constraints in providing equitable access to care is the language barrier between providers and the patients they serve. For Medicaid agency call centers, there aren’t enough agents to support communication in all the languages requested by a state government.

Some states want to support nearly 20 languages in the call center but have agents who speak only two or three languages. The traditional approach of recording voices is expensive and also hampers the state’s ability to quickly change the messaging as appropriate for each member’s concerns. Relying on manual methods to record and create content in different languages can hinder the timeliness of implementation. The translation services offered in several Medicaid agency call centers add several hours of wait time for those seeking care.
&nbsp;
However, there’s a simple alternative. Agencies can use artificial intelligence (AI) and omnichannel contact center solutions from [Amazon Web Services (AWS)](https://aws.amazon.com/) to create a multilingual contact center that helps break down the language barrier between Medicaid members and call center agents.
&nbsp;
In this post, we will explore how to build a multilingual contact center that can provide near real-time assistance for a non-English-speaking constituent from an English-speaking agent.

## Solution overview

This walkthrough depicts an AWS Cloud-based solution that supports public sector organizations in providing near real-time translation chat support through [Amazon Connect](https://aws.amazon.com/connect/), [Amazon Transcribe](https://aws.amazon.com/transcribe/), and serverless code through [AWS Lambda](https://aws.amazon.com/lambda/). Translations that would take hours to complete manually are performed in moments and read back, in life-like speech, and in a member’s chosen language through [Amazon Polly](https://aws.amazon.com/polly/). Figure 1 is an architectural diagram of the solution.

![alt text](https://github.com/aws-samples/amazon-connect-live-agent-translation/blob/main/Architecture.jpg)

_Figure 1. Technical architecture of the multilingual contact center solution described in this post._ ![Technical architecture of the multiLingual contact center quickstart solution. ]

1. The constituent calls the main contact center number. The greeting prompts the caller to select a language. The caller is asked to speak in the language of their choice.
2. The constituent’s voice is streamed near real time using [Amazon Kinesis Data Streams](https://aws.amazon.com/kinesis/data-streams/).
3. Amazon Connect contact flow triggers a Lambda function to convert voice to text.
4. Amazon Transcribe is used to transcribe the constituent’s spoken words into text.
5. Transcribed text is stored in [Amazon Simple Storage Service (Amazon S3)](https://aws.amazon.com/s3/) and [Amazon DynamoDB](https://aws.amazon.com/dynamodb/).
6. Amazon Connect Contact Control Panel (CCP) gets the transcribed text printed in the window.
7. The transcribed text is translated to English using [Amazon Translate](https://aws.amazon.com/translate/) and displayed in the CCP.
8. The agent reviews the text and types the response in the CCP.
9. Amazon Translate is used to convert the English text written by the agent into the language chosen by the constituent. Amazon Polly is used to create a voice file for the translated text.
10. The translated voice is played back to the constituent as a response to the question they asked.

## Solution walkthrough: Building a multilingual contact center for Medicaid agencies

The steps below will guide you through the process of deploying a multilingual contact center. Section 1 will set up the foundation infrastructure needed to support the solution while Section 2 will walkthrough the steps to configure the Amazon Connect instance. Section3 walks through testing the deployed solution.


## Prerequisites

1. Have an [AWS account](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fportal.aws.amazon.com%2Fbilling%2Fsignup%2Fresume&client_id=signup)
2. Have an understanding of Amazon Connect, Lambda, and [AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam/)
3. Have permissions to create and modify Lambda functions
4. Configure an Amazon Connect instance for inbound and outbound calls, and claim a phone number after you create your instance. The [Get started with Amazon Connect documentation](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-connect-get-started.html) (the first two steps) provides valuable background knowledge for this process.
5. [Turn on data streaming](https://docs.aws.amazon.com/connect/latest/adminguide/data-streaming.html) on the Amazon Connect instance.
6. [Turn on live media streaming](https://docs.aws.amazon.com/connect/latest/adminguide/enable-live-media-streams.html) on the Amazon Connect instance


##  Section 1: Deploy [AWS CloudFormation](https://aws.amazon.com/cloudformation/) templates  

1. Navigate to the GitHub repo for the template.
    1. Clone the repo
    2. Navigate to the repository folder on your local machine
        1.  Create a .zip of the following files/folders:
            1. cloudformation/asset.7b1f3c122a53128c55239bc2e97800299bcce83e3fb7394b79ed0b35af5757ee/mlcc-transcribe-polly.py
    3. [Create a new Amazon S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) and upload the folders named CloudFormation and CCP from the cloned repo.
2. Navigate to the CloudFormation dashboard within the AWS console and [create a CloudFormation stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html) using the file named “MultiLingualCC.yaml.” The following parameters are needed to be provided for the stack to launch.
    1. **Stack name** – The stack name is an identifier that helps you find a particular stack from a list of stacks. A stack name can contain only alphanumeric characters (case-sensitive) and hyphens. It must start with an alphabetic character and can't be longer than 128 characters.
    2. Amazon Connect instance ID (Ensure that it is entered accurately in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).
    3. **Call audio bucket name** – Enter the (globally unique) name you would like to use for the Amazon S3 bucket where you will store the audio files and the sample contact flow. This template will fail to deploy if the bucket name you choose is currently in use.
    4. **Website bucket name** – Enter the (globally unique) name you would like to use for the Amazon S3 bucket where you will store the website assets and the sample contact flow. This template will fail to deploy if the bucket name you choose is currently in use.
    5. **Resources bucket** – This is the bucket you created in step 1c.
    6. **audioFilePrefix** – The Amazon S3 prefix where the audio files will be saved (must end in "/").
    7. **CloudFront Price Class** – Specify the CloudFront price class. See [pricing details for more information](https://aws.amazon.com/cloudfront/pricing/%20).
    8. **Compute type** – Specify whether to use [AWS Fargate](https://aws.amazon.com/fargate/) or Lambda for transcribing call audio to text. The solution, by default, uses a Lambda function to transcribe call audio consumed from [Amazon Kinesis Video Streams](https://aws.amazon.com/kinesis/video-streams/?amazon-kinesis-video-streams-resources-blog.sort-by=item.additionalFields.createdDate&amazon-kinesis-video-streams-resources-blog.sort-order=desc). Lambda has a maximum run time of 15 minutes per invocation, whereas Fargate has no such limits and can run as long as the call is connected.
    9. **rawAudioUploadPrefix** – The Amazon S3 prefix where raw/wav (audio/L16; mono; 8 kHz) audio recordings may be uploaded if you want to process an audio file compared to making a phone call and streaming from Kinesis Video Streams. This parameter is used for testing or for real-time transcription of audio files. This will only work with single-channel files (mono).
    10. **sessionDuration** – The maximum duration of the role session (in seconds). You can give a value from 900 seconds (15 minutes) to 3,600 seconds (1 hour). This is the maximum call duration before the customer interaction must be processed.
3. Create the stack.
4. After the stack is successfully launched, note the following outputs. It could take a few minutes for the stack to launch the solution.
    1. **cloudfrontEndpoint** – This is the CloudFront URL you will use to access the agent portal. You can find this in the **Output** tab for the stack.
5. Create a lambda layer by cloning and following up the instructions on the following repository  <https://github.com/amazon-connect/amazon-connect-audio-utils/tree/master>  Keep in mind that docker is required for this step. 
6. Add the layer to the lambda function with the following name HSSDemo-Transcribe-Polly


## Section 2: Configuring Amazon Connect instance  

1. Log in to the Amazon Connect instance using the admin user you created while launching the instance.
2. Select the telephone number you claimed and assign the contact flow “mlccKvsStream,” as shown in Figure 2.

![alt text](https://github.com/aws-samples/amazon-connect-live-agent-translation/blob/main/AmazonConnectContactFlowAssignment.jpg)
_![Amazon Connect contact flow assignment.]Figure2: Screenshot of Amazon Connect contact flow assignment._


## Section 3: Testing  

1. Use the CloudFront URL noted in Section 1, step 4a to access the agent CCP.
2. Call the claimed telephone number and choose the language.
3. As you speak, note the agent CCP update with transcribed text in English.
4. As an agent, type the response and select **Submit**.
5. Observe the text translated to the language you chose and delivered back to you on the call using voice.


## Conclusion

This walkthrough deploys a multilingual contact center that allows callers to talk in their preferred language without requiring the state to hire agents to cover all the languages.

AWS is ready to support Medicaid agencies as they transform to meet COVID-19 Public Health Emergency (PHE) unwinding efforts. [Contact the AWS Public Sector Team to learn more](https://aws.amazon.com/government-education/contact/?trkCampaign=ps&trk=ps_blog_body).

Health and human services agencies across the country are using the power of AWS to unlock their data, improve citizen experience, and deliver better outcomes. Learn more at [Health and Human Services Cloud Resources](https://aws.amazon.com/stateandlocal/health-and-human-services/cloud-resources/?awsm.page-health-and-human-services-experts-all=1). Learn how governments use AWS to innovate for their constituents, design engaging constituent experiences, and more by visiting the [AWS Cloud for State and Local Governments](https://aws.amazon.com/stateandlocal/) hub.
