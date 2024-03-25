Vignesh Srinivasan

Vignesh Srinivasan is a senior solutions architect at Amazon Web Services (AWS). He spent a decade working with CMS, including helping to implement the Federal Health Exchange as part of the Affordable Care Act. He was also an integral part of the team responsible for fixing the healthcare.gov system and eventually successfully migrating the system to AWS. His passion is in enabling states to make their own decisions. Vignesh has a master’s degree from Rochester Institute of Technology and an MBA from the University of Maryland, in addition to several professional certifications.

Sebastian Alvarez Vasquez

Sebastian is a Solutions Architect, Amazon Connect Specialist. He has been helping customer implement their Contact Center solutions for over 15 years all over the world. On his spare time, Sebastian likes to spend time with his family and enjoy the beautiful Colorado together.

--------------------------------------------------------------------------------------------------------------------------------------------------
One of the biggest constraints in providing equitable access to care is the language barrier between care providers and those they serve. For Medicaid agency call centers, there aren’t enough agents to support communication in all the languages requested in the state. Some states want to support nearly 20 languages in the call center, but have agents who speak only 2-3 languages. The traditional approach of recording voices is expensive and also hinders the ability to quickly change the messaging as appropriate for each member’s concerns. Relying on manual methods to record and create content in different languages can hinder timeliness of implementation.Translation services offered in several Medicaid agency call centers adds several hours of wait time to the constituent. 
 
However, there’s a simple alternative. Agencies can use artificial intelligence (AI) and omnichannel contact center solutions from Amazon Web Services (AWS) to create a multi-lingual contact center that helps break down the language barrier between Medicaid members and call center agents. 
 
In this blog post, learn how to build a multi-lingual contact center that can provide near real-time assistance for a non-English speaking constituent from an English speaking agent. 

Solution overview: Building a multi-lingual contact center for Medicaid agencies

This walkthrough depicts an AWS Cloud-based solution that supports public sector organizations in providing near real-time translation chat support through Amazon Connect, Amazon Transcribe, and serverless code via AWS Lambda. Translations that would otherwise need hours to complete manually can take place in moments as translations are read back, in life-like speech, and in a member’s chosen language through Amazon Polly.


Figure 1. Technical architecture of the MultiLingual Contact Center Quickstart solution. 


1. The constituent calls the main contact center number. The greeting prompts the caller to select a language. The caller is asked to speak in the language of their choice. 
2. The constituent’s voice is streamed near real time using Amazon Kinesis Streams.
3. Amazon Connect Contact Flow triggers AWS Lambda function to convert voice to text.
4. Amazon Transcribe is used to transcribe constituent’s spoken words into text.
5. Transcribed text is stored in Amazon S3 and Amazon DynamoDB.
6. Amazon Connect Contact Control Panel (CCP) gets the transcribed text printed in the window.
7. The transcribed text is translated to English using Amazon Translate and displayed in CCP. 
8. Agent reviews the text and types the response in the CCP. 
9. Amazon Translate is used to convert the english text written by the agent to the language chosen by the constituent. Amazon Polly is used to create a voice file for the translated text.
10. Translated voice is played back to the constituent as a response to the question they asked.



Solution deployment

For this walkthrough, you must have the following prerequisites: 

1. An AWS account
2. Understanding of Amazon Connect, AWS Lambda, and AWS Identity and Access Management (IAM)
3. Permissions to create and modify Lambda functions
4. Configure an Amazon Connect instance for inbound and outbound calls, and claim a phone number after you create your instance. The Getting Started with Amazon Connect documentation (first two steps) provide valuable background knowledge for this process.
5. Enable Data streaming on Amazon Connect Instance.
6. Enable Live Media streaming on Amazon Connect Instance



 Section 1: Deploy AWS CloudFormation templates

1. Navigate to the GitHub repo for the template.
    1. Clone the repo
    2. Navigate to the repository folder on your local machine
        1.  zip the following files/folders 
            1. cloudformation/asset.7b1f3c122a53128c55239bc2e97800299bcce83e3fb7394b79ed0b35af5757ee/mlcc-transcribe-polly.py
            2. cloudformation/asset.7d36748ef52dddfb032d45c847b2631b5f0c9e2ab427d2fb6155559b07eefe18/connectaudioutils  this will have to be a manual step
    3. Create a new s3bucket and upload the folders named CloudFormation and CCP from cloned repo.
2. Navigate to the CloudFormation dashboard within the AWS console and create a CloudFormation stack using the file named - “MultiLingualCC.yaml”. The following parameters are needed to be provided for the stack to launch.
    1. Stack name: The stack name is an identifier that helps you find a particular stack from a list of stacks. A stack name can contain only alphanumeric characters (case-sensitive) and hyphens. It must start with an alphabetic character and can't be longer than 128 characters.
    2. Amazon Connect Instance ID (Ensure you it is entered accurately in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx ).
    3. Call Audio Bucket Name: Enter the (globally unique) name you would like to use for the Amazon S3 bucket where we will store the audio files, and the sample contact flow. This template will fail to deploy if the bucket name you chose is currently in use. 
    4. Website Bucket Name: Enter the (globally unique) name you would like to use for the Amazon S3 bucket where we will store the website assets and the sample contact flow. This template will fail to deploy if the bucket name you chose is currently in use. 
    5. Resources Bucket: This is the bucket you created in step#1c.
    6. audioFilePrefix: The Amazon S3 prefix where the audio files will be saved (must end in "/")
    7. CloudFront Price Class: Specify the CloudFront price class. See pricing details. 
    8. Compute Type: Specify whether to use AWS Fargate or AWS Lambda for transcribing call audio to text. The solution, by default, uses an AWS Lambda function to transcribe call audio consumed from Kinesis Video Streams. Please note that Lambda has a maximum run time of 15 minutes per invocation whereas Fargate has no such limits and can run as long as the call is connected.
    9. rawAudioUploadPrefix: The Amazon S3 prefix where raw/wav (audio/L16; mono; 8 kHz) audio recordings may be uploaded in the event you would like process an audio file vs making a phone call and streaming from KVS. Mainly for testing, or for realtime transcription of audio files. This will only work with single channel files (mono). 
    10. sessionDuration: The maximum duration of the role session (in seconds): You can give a value from 900 seconds (15 minutes) to 3600 seconds (1 hour). This is the maximum call duration limit until which the customer interaction in Amazon Connect need to be processed by this solution.
3. Create the stack.
4. After the stack is successfully launched, note the following outputs. It could take a few minutes for the stack to launch the solution. 
    1. cloudfrontEndpoint - This is the cloudfront URL you will use to access the agent portal. You can find this in the “output” tab for the stack. 
5. Create a lambda layer by cloning and following up the instructions on the following repository  https://github.com/amazon-connect/amazon-connect-audio-utils/tree/master.  Keep in mind that docker is required for this step.
6. Add the layer to the lambda function with the following name  HSSDemo-Transcribe-Polly




Section 2: Configuring Amazon Connect Instance

1. Login to Amazon connect instance using the admin user you created while launching the instance.
2. Click on the telephone number you claimed and assign the contact flow “mlccKvsStream”.


Section 3: Testing

1. Use the cloudfront URL noted above to access the agent CCP. 
2. Call the claimed telephone number and choose the language.
3. As you speak, note the agent CCP update with transcribed text in english.
4. As an agent, type the response and click submit.
5. Observe the text translated to the language you chose and delivered back to you on the call using voice.

Conclusion


 This walkthrough helps deploy a multi-lingual contact center using which a member can continue to talk in the language they feel most comfortable, without the state needing to hire agents to cover all the languages. 

AWS is ready to support Medicaid agencies as they transform to meet Public Health Emergency (PHE) unwinding efforts. Contact the AWS Public Sector Team to learn more.

Health and human services (HHS) agencies across the country are using the power of AWS to unlock their data, improve citizen experience, and deliver better outcomes. See more Health and Human Services Cloud Resources here. Learn more about how governments use AWS to innovate for their constituents, design engaging constituent experiences, and more at the AWS Cloud for State and Local Governments hub.
