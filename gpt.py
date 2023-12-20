import openai
import os
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
# openai_api_key = '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'
model = "gpt-4-1106-preview"
filecontent = """
S.No	Indicator Type	Indicator Category	 Indicator Values	Alternative Value	Score (If hear once)	Time Constraint	Total score	Scoring Weightage	Start Time (mm:ss)	End Time (mm:ss)
1	Introduction	Greetings	Hi 	Hello	If heard once score to be given is 1.	Yes - First Stage	8	8%	00:00	00:02
				Hey						
				Hello there						
		Name	My Name is	I am 	If heard once score to be given is 2.	Yes - First Stage				
				This is						
		Title and Roles	Sales 	Sales Representative	If heard once score to be given is 1.	Yes - First Stage				
				Sales Rep						
				Sales Executive						
			Account	Account Executive	If heard once score to be given is 2.	Yes - First Stage				
				Account Manager						
		Responsibilities	Responsibiltiy	I am responsible for	If heard once score to be given is 2.	Yes - First Stage				
				I am in charge of						
				I take care of						
2	Agenda Setting	Agenda Setup for the meeting	The reason for my call today is	I'm reaching out today to discuss	If heard once score to be given is 4.	Yes - Second Stage	8	8%	00:02	00:03
				I wanted to connect with you about						
				My purpose in calling is to talk about						
		Rapport Building	Have I caught you at a good time?	Is now a convenient moment for us to chat?	If heard once score to be given is 4.	Yes - Second Stage				
				Do you have a few moments to discuss?						
				Is this a suitable time for us to talk?						
				Would you prefer to speak now or should I schedule a better time?						
3	Company Introduction	Company Offerings / Services	Solutions	We specialize in providing	If heard once score to be given is 5.	Yes - Third Stage	10	10%	00:03	00:06
				Core offerings						
				Specialized services						
				Flagship solutions						
				Range of services						
				Tailored offerings for your need						
		Company Stats - Revenue / Global Presence / Employee Strength	Shared about achievements	Achieved	If heard once score to be given is 5.	Yes - Third Stage				
				Global presence in						
				Expanded operations to						
				Strong presence in						
4	Product / Service	Product Demo/ Information	Let me show you	I'd like to demonstrate	If heard once score to be given is 7.	Yes - Third Stage	14	14%	00:06	00:16
				how it works						
				walkthrough						
				a live demo						
				Allow me to present						
			Features	Key Features	If heard once score to be given is 7.	Yes - Third Stage				
				Benefits						
				Unique selling point						
				use case						
				what sets it apart						
5	Probing	Challenges and Pain Points	What difficulties are you currently facing	What pain points do you have 	If heard once score to be given is 5.	Yes - Fourth Stage	20	20%	00:16	00:21
				Can you tell me about your challenges						
				Whats been causing issues						
				Are there any pain points in your current setup						
		Ongoing and upcoming projects or initiatives	What projects are you currently working on	Can you share your ongoing initiatives	If heard once score to be given is 5.	Yes - Fourth Stage				
				Any upcoming projects 						
				Your current initiatives						
		Current vendors/ service providers	your current service providers	Are you working with any vendors currently	If heard once score to be given is 5.	Yes - Fourth Stage				
				your existing partners						
				What companies are you currenlty outsourcing to						
		Current Platforms or tools being used	What platforms/tools are you using right now?	Tools that you are currently utilizing	If heard once score to be given is 5.	Yes - Fourth Stage				
				tell me about the software you're using in your operations						
				what tech solutions do you currently employ						
6	Next Steps Discussion	Follow-up conversations/ next steps	Next discussion	Moving forward	If heard once score to be given is 4.	Yes - Fifth Stage	16	16%	00:21	00:25
				Next Steps						
				Continuing our conversation						
		Follow-up Date and Time	Reconnet	when can we reconnect	If heard once score to be given is 4.	Yes - Fifth Stage				
				can we schedule our next talk						
				choosing a follow-up date						
				what time works for you						
		Proposed POC	I will be your main point of contact	you can reach out to me directly	If heard once score to be given is 4.	Yes - Fifth Stage				
				I'm your designated contact						
				Feel free to contact me anytime						
				I will be your go to person						
		Decision Maker	decision making	Who will be the decision maker	If heard once score to be given is 4.	Yes - Fifth Stage				
				Who will be making the final call						
				Let's involve the decision maker						
				Is there someone else from your side						
7	Objection Handling	Addressing Objections	I understand your concern	That's a valid point	If heard once score to be given is 8.	Yes - Sixth Stage	24	24%	00:25	00:30
				I hear what you are saying						
				I appreciate your feedback						
				Let me address that						
				I'm here to clarify						
		Providing Explanations and References	Let me explain how our solution	here's how others have tackeled this issue	If heard once score to be given is 8.	Yes - Sixth Stage				
				our case study demonstrate						
		Offering Solutions to overcome objections	to approach this problem	One way to solve this problem	If heard once score to be given is 8.	Yes - Sixth Stage				
				whatif we						
				how about considering						
				A potential solution might be						"""

instructions = "You are to analyze a conversation of a sales representative and score it based on specific criteria. Also take into consideration the time constraint. Here are the scoring guidelines:"

def gpt_response(convo):
    convo = str(convo)
    conversation = [
        {
            "role": "system",
            "content": instructions,
        },
    {
            "role": "system",
            "content": filecontent,
        },
        {
            "role": "system",
            "content": convo,
        },
    ]
    # Call to OpenAI chat API
    response = openai.ChatCompletion.create(
        model=model,
        messages=conversation,
        api_key=openai_api_key,  # Use the API key from the environment variable
    )

    # Get the answer from OpenAI
    answer = (response.get("choices", [{}])[0])
    # print("Received answer from OpenAI:", answer)
    content = answer.get("message", {}).get("content", "")

    print("Extracted content:", content)
    return content