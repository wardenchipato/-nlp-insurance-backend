**CHAPTER 1: PROBLEM IDENTIFICATION**

**1.1 Introduction**

Road accidents keep killing people. Lots of them. Every single year, around 1.19 million men, women, and children die on the world's roads. That is according to the World Health Organization (WHO, 2023). Millions more get hurt, sometimes badly. Some never fully recover.

Here is the thing. Poorer countries get the worst of it. Zimbabwe is one of them. The roads can be rough, and safety rules are not always followed or enforced.

Let me give you some numbers. The Zimbabwe Republic Police and the Traffic Safety Council of Zimbabwe keep track of this stuff. In 2023 alone, there were 52,288 accidents. Two thousand and ninety nine people died (ZRP, 2024; TSCZ, 2024). Do the math. That is about five or six deaths every day. Behind each number is a family that lost someone.

Then there is the money side. Accidents cost a fortune. Insurance companies pay out huge sums. Families struggle with medical bills. Governments spend on emergency services and road repairs.

Motor insurance tries to help with the financial pain. Insurers want to know who is likely to crash and who is not. They set prices based on that guess. Traditionally, they look at simple stuff. How old are you? Where do you live? What car do you drive? Have you claimed before? (Verbelen et al., 2018)

Those things matter, sure. But they miss a lot. They do not tell you if someone was driving like a maniac or if the roads were icy and dark (Cheng et al., 2022).

That is where NLP comes in. NLP stands for Natural Language Processing. Fancy name, but the idea is simple. It is software that reads text and understands what it means. Researchers have shown that NLP can dig through accident reports and pull out useful clues. Words like "speeding," "drunk," "fog," "pothole." Those clues point to risky behaviour (Kumar et al., 2023).

So what if you added those clues to the traditional model? You might get a better picture. You might spot the dangerous drivers more accurately.

I wanted to test this idea. So I built a working system. The backend runs on FastAPI. The frontend uses React and Tailwind CSS. You feed it policyholder data and accident text. It runs NLP. It spits out a risk score and a classification. The big question is whether something like this could work in Zimbabwe. Nobody has really tried it here before (Adeyemi & Adebayo, 2024).

**1.2 Background of the Study**

Risk assessment is the backbone of insurance. Get it right, and everyone wins. Get it wrong, and you either scare off good customers with high prices or lose money on bad ones.

Most insurers today rely on structured data. That means information you can put in a spreadsheet. Age. Car type. Claims history. Simple stuff (Verbelen et al., 2018).

But here is what bothers me. Accident reports are full of details that never make it into those spreadsheets. A cop writes down what happened. "Driver was speeding in heavy rain." "Lost control on a gravel road after dark." Those little details tell a story. They explain why the crash happened.

Two drivers can look identical on paper. Same age. Same car. Same neighbourhood. But one was driving recklessly in a storm. The other just had bad luck with a flat tyre. The spreadsheet cannot tell them apart. The accident report can (Cheng et al., 2022).

NLP can read those reports. It can clean up the text. Pull out keywords. Classify what kind of risk each phrase represents (Kumar et al., 2023).

Once you have those extracted features, you can add them to your prediction model. Studies from the US and Europe show this works pretty well (Backlund & Ohman, 2023).

But Zimbabwe? Not much research here. Almost none, actually. That gap is exactly why I am doing this study (Adeyemi & Adebayo, 2024).

**1.3 Statement of the Problem**

Here is the problem in plain English.

Zimbabwean insurers still use old methods. They look at driver age. Vehicle age. Engine size. Where you live. How many claims you have made (Verbelen et al., 2018).

These factors are okay. But they are not enough. They miss everything that matters about what actually happened during the crash (Cheng et al., 2022).

Imagine two drivers. One is young, drives a sports car, and has two previous claims. Looks bad, right? But maybe that driver was being careful and the accident was not their fault. Now imagine an older driver. Clean record. Drives a sensible sedan. But they were speeding through fog when they crashed. The structured data would flag the first driver as high risk and the second as low risk. That would be completely backwards.

That is what I am talking about. When insurers ignore the story behind the numbers, they get risk profiles that are wrong. Premiums get set at the wrong price. Unexpected claims pile up (Kumar et al., 2023).

Studies from elsewhere show that NLP can find hidden patterns in accident narratives. It can improve predictions significantly (Kwayu, 2021; Backlund & Ohman, 2023).

But in Zimbabwe, nobody is really using this stuff. The technology is available, but the adoption is not there (Adeyemi & Adebayo, 2024).

So the problem is simple. Zimbabwean insurers are leaving valuable information on the table. They are not capturing behavioural and environmental clues that could make their pricing much smarter. This study tries to fix that by building a hybrid model. Structured data plus NLP features. Then we see if it works (Cheng et al., 2022; Kumar et al., 2023).

**1.4 Research Objectives**

**Main Objective**

The main goal is to find out whether NLP features from accident reports actually help predict motor insurance risk more accurately (Cheng et al., 2022; Kumar et al., 2023).

**Specific Objectives**

I have three specific things I want to accomplish.

First, I want to understand what NLP techniques are already being used in motor insurance to pull risk indicators out of accident narratives. What works? What does not? (Kumar et al., 2023)

Second, I want to build a simple baseline model. This one will use only structured data. No NLP. Just age, vehicle type, claims history, and so on (Verbelen et al., 2018).

Third, I want to build a second model. This one adds the NLP features to the structured data. Then I can compare the two and see if the NLP version actually performs better (Cheng et al., 2022).

For that third objective, I will run both models on the same test data. The system calculates risk scores and shows the percentage improvement, if any, from adding the NLP features (Cheng et al., 2022; Kwayu, 2021).

**1.5 Research Questions**

I am trying to answer three main questions in this study.

Question one. What NLP techniques are currently used in motor insurance to pull risk indicators out of accident reports? (Kumar et al., 2023)

Question two. How do you build a rule-based risk model using only structured data? What are the steps? (Verbelen et al., 2018)

Question three. How much improvement do you actually get when you add NLP features to the mix? Is it worth the extra effort? (Cheng et al., 2022; Kwayu, 2021)

**1.6 Research Hypotheses**

Every good study needs hypotheses. Here are mine.

The null hypothesis, which I call H₀, says that adding NLP features does not make a real difference. The accuracy stays the same (Cheng et al., 2022).

The alternative hypothesis, H₁, says the opposite. Adding NLP features does improve accuracy. Significantly (Cheng et al., 2022; Kumar et al., 2023).

I will be honest. I am rooting for H₁. Otherwise, what was the point of all this work?

**1.7 Justification and Significance of the Study**

Why does this study matter? Let me count the reasons.

First, the practical reason. If NLP helps insurers price risk more accurately, everybody benefits. Safe drivers pay less. Risky drivers pay what they should. The company does not get surprised by huge unexpected claims (Cheng et al., 2022; Kumar et al., 2023).

Second, underwriters can make better calls. If the system flags someone because their accident report mentions "drunk driving" and "speeding," the insurer might add restrictions or charge a higher premium (Kumar et al., 2023; Verbelen et al., 2018).

Third, this study proves that NLP is not just academic theory. It can work in the real world. Even in a developing country with limited resources (Backlund & Ohman, 2023; Verbelen et al., 2018).

Fourth, there is a research gap. Nobody has really studied this in Zimbabwe before. This study provides local evidence that local insurers can actually use (Adeyemi & Adebayo, 2024).

Fifth, and this one is broader. If we get better at identifying risky driving behaviour and dangerous conditions, maybe we can also help with road safety campaigns. Fewer accidents mean fewer deaths. That benefits everyone, not just insurance companies (WHO, 2023; TSCZ, 2024).

**1.8 Assumptions**

I had to make some assumptions going into this. Let me list them.

I assume that accident reports actually contain useful risk indicators. If the reports are vague or empty, the whole approach falls apart (Cheng et al., 2022).

I also assume that NLP can handle messy text. Accident reports are not always well written. There are typos. Abbreviations. Local slang. I am hoping the NLP tools can still do a decent job despite the mess (Kumar et al., 2023).

Another assumption. Combining structured data with NLP features will not cause overfitting. The model should still perform well on new data it has never seen before (Verbelen et al., 2018).

Finally, I assume my dataset is reasonably representative of Zimbabwean accidents in general. If it is not, my results might not apply to the wider population (ZRP, 2024; TSCZ, 2024).

**1.9 Limitations and Challenges**

I ran into several problems along the way. Here they are.

Data access was hard. Accident reports contain sensitive information. People do not just hand them over. Many organisations said no (Adeyemi & Adebayo, 2024).

The quality of the reports varied wildly. Some were detailed and well written. Others were short, sloppy, and missing key facts. That inconsistency affects how well NLP can do its job (Cheng et al., 2022; Kumar et al., 2023).

Informal language was another headache. People use abbreviations and local expressions that standard NLP models do not understand. Training the models to recognise this language would take more time and more data (Kumar et al., 2023; Adeyemi & Adebayo, 2024).

Computing power was also an issue. I do not have access to a supercomputer. I could not train massive models or run huge experiments. I had to work with what I had (Adeyemi & Adebayo, 2024).

**1.10 Scope and Delimitation of the Study**

Let me be clear about what this study covers and what it does not.

I focused only on motor insurance in Zimbabwe. Private and commercial vehicles. Not motorcycles or public transport (ZRP, 2024; TSCZ, 2024).

I used historical data. Old accident reports and policyholder records. I applied NLP to extract features. I used a rule-based model, not complex machine learning (Kumar et al., 2023; Cheng et al., 2022).

Now for what I did not do. I did not build a real-time system. I did not look at health insurance or property insurance. Those are completely different (Verbelen et al., 2018).

**1.11 Definition of Terms**

Some terms might be unfamiliar. Here is what they mean in plain language.

**Natural Language Processing (NLP).** Software that reads human language and understands it (Kumar et al., 2023).

**Risk Assessment.** The process of guessing how likely someone is to make an insurance claim and how much it might cost (Verbelen et al., 2018).

**Structured Data.** Information that fits neatly into tables or spreadsheets. Age. Car type. Number of claims (Cheng et al., 2022).

**Unstructured Data.** Messy information that does not have a fixed format. Like a police officer's written accident report (Cheng et al., 2022).

**Feature Extraction.** Pulling useful pieces of information out of raw data and turning them into something a model can use (Kumar et al., 2023).

**Rule-Based Model.** A prediction system that uses if-then rules. If age is under 25, add points to the risk score (Verbelen et al., 2018).

**1.12 Organisation of the Study**

This dissertation has five chapters. Here is what each one does.

**Chapter 1** sets everything up. It introduces the topic. Gives background. States the problem. Lists objectives and questions. Explains the scope (Cheng et al., 2022).

**Chapter 2** looks at what others have done. It reviews the literature on motor insurance risk and NLP applications (Kumar et al., 2023; Backlund & Ohman, 2023).

**Chapter 3** explains the methodology. How I designed the system. What tools I used. How I built the model (Verbelen et al., 2018).

**Chapter 4** shows the results. What happened when I tested the system with real data (Cheng et al., 2022).

**Chapter 5** concludes everything. I discuss what I learned. What the limitations were. Where future research could go (Adeyemi & Adebayo, 2024).

**CHAPTER 2: LITERATURE REVIEW**

**2.1 Introduction**

The growing complexity of motor insurance risk assessment has necessitated the adoption of advanced analytical approaches capable of integrating both structured and unstructured data. Traditional actuarial models have historically relied on structured variables such as age, vehicle type, geographic location, and claims history to estimate risk. While these variables provide measurable and standardised indicators, they have been widely criticised for failing to capture behavioural and contextual factors embedded within accident narratives (Verbelen, Antonio & Claeskens, 2021).

Why did insurers stick with these classical models? Because structured data was easy to get and easy to process. Actuaries could plug it into statistical methods like generalised linear models and get consistent results (Boodhun & Jayabalan, 2018). But here is the problem. Accidents do not happen in spreadsheets. They happen because a driver got distracted, or the weather turned bad, or the road was poorly maintained. Those factors are qualitative. They do not fit neatly into columns and rows. When you leave them out, you end up underestimating risk (Li, Xu & Zhao, 2023).

This limitation has real consequences. Premiums get mispriced. Good drivers might pay too much. Bad drivers might pay too little. In developing markets, where insurers already operate on thin margins, this can be devastating. It leads to adverse selection and weakens the whole risk pooling system (Verbelen et al., 2021).

So what is the solution? Natural Language Processing, or NLP. It is a branch of artificial intelligence that reads human language and turns it into something machines can process. Researchers have shown that NLP can pull useful information out of accident narratives, transforming messy text into clean, structured features (Cheng, Liu & Wang, 2022; Hassan, Bashir & Mahmood, 2022).

But here is the catch. Adoption of NLP in motor insurance is not happening evenly around the world. Rich countries are moving ahead. Developing countries like Zimbabwe are lagging behind. The infrastructure is not there. The data is not always available (Adeyemi & Adebayo, 2024).

This chapter critically reviews literature on motor insurance risk assessment, with a focus on NLP techniques used to extract risk indicators from accident narratives, and identifies research gaps that justify the current study.

**2.2 Relevant Theories of Risk Assessment**

Before we dive into the research, let me lay out the theoretical foundation. A few key frameworks support modern motor insurance risk assessment.

First is Expected Utility Theory. The idea is simple. Insurers set premiums based on what they expect to pay out in claims, plus a little extra for risk. To do that accurately, they need good estimates of loss distributions (Verbelen et al., 2021).

Then there is Asymmetric Information Theory. This one explains what happens when the insurer knows less than the policyholder. When premiums do not reflect individual risk profiles, high-risk individuals are more likely to buy insurance. That is called adverse selection, and it is a big problem (Li et al., 2023).

More recently, researchers have proposed something called Multidimensional Risk Factor Analysis. The idea here is that accidents do not have single causes. They result from the interaction of many factors. The framework identifies six distinct dimensions. Behavioural covers driver actions. Environmental covers weather and road conditions. Temporal covers time of day and season. Vehicle covers condition and type. Location covers geographic risk. Claims History covers past severity patterns (Panboonyuen, 2026; Zhang, Chen & Li, 2022).

Why does this matter for my study? Because each of these dimensions contains both structured and unstructured data. NLP can help pull out the unstructured parts (Hassan et al., 2022).

**2.3 Empirical Literature on Motor Insurance Risk Assessment**

Let me walk you through what researchers have actually found when they tested these ideas.

Verbelen, Antonio and Claeskens (2021) ran a study using GLMs with only demographic and vehicle variables. Their model explained only 62% of the variance in claim frequency. That means nearly 40% of what drives claims was left on the table. Not great.

Boodhun and Jayabalan (2018) tried something different. They compared multiple machine learning approaches for life insurance risk prediction. Neural networks achieved 89% accuracy. Traditional logistic regression only managed 78%. The lesson? Complex interactions between risk factors need non-linear models to capture them.

More recently, researchers have started adding unstructured data to the mix. Cheng, Liu and Wang (2022) looked at 50,000 insurance claims. They added text mining features from claim descriptions to their models. Predictive accuracy for claim severity improved by 23%. Specific keywords like "high speed," "distracted," and "poor visibility" turned out to be strong predictors of severe claims.

Li, Xu and Zhao (2023) went even further. They applied BERT, a powerful transformer model, to financial risk analysis. They achieved F1 scores of 0.91 for risk classification tasks. But they also noted something important. Transformer models need serious computing power. That is fine if you are Google. Not so fine if you are a small insurer in Zimbabwe.

Hatzesberger and Nonneman (2026) looked at generative AI. They presented four case studies showing that large language models can extract predictive features from unstructured claim descriptions. They also found that vision-enabled LLMs could classify car damage types from images. The frontier is multimodal.

Poufinas and colleagues (2023) evaluated different machine learning methods for forecasting motor insurance claims. Their finding? Ensemble methods like Random Forests and Gradient Boosting consistently outperformed GLMs, especially for skewed, high-severity claims.

The literature indicates a clear trend: hybrid models combining structured and unstructured data outperform traditional approaches. However, most studies are conducted in high-income countries with access to large labelled datasets and advanced computing infrastructure, creating a significant research gap for developing contexts (Adeyemi & Adebayo, 2024).

**2.4 Motor Insurance in Zimbabwe: Context and Challenges**

Let me shift focus to Zimbabwe specifically.

Motor insurance is important there. The Insurance and Pensions Commission, or IPEC, oversees the industry. The Road Traffic Act makes third-party insurance compulsory. Every registered vehicle needs basic coverage (NewsDay, 2025).

But the industry has serious problems. Recent data from the Zimbabwe Republic Police shows 2,412 road traffic accidents during the 2025/26 festive season alone. Eighty-seven of those were fatal. One hundred people died. The Insurance Council of Zimbabwe coordinated emergency response for 226 verified incidents. Most accident reports came in between 4 pm and 9 pm (The Financial Gazette, 2026).

Two main types of coverage exist in Zimbabwe. Third Party Liability is the legal minimum. It covers damage to others. Comprehensive Cover is more complete. It covers your own vehicle, third party liability, passenger injuries, natural disasters, and theft (NewsDay, 2025).

Here is the challenge. Most insurers still rely on traditional underwriting methods. But there are some positive signs. Telematics and GPS tracking systems are starting to appear. These record driving habits and assess individual risk more accurately. The Insurance Council of Zimbabwe has also launched highway emergency response initiatives. They are becoming more aware of data-driven risk management (The Financial Gazette, 2026).

Still, NLP integration is minimal. Data is fragmented. The economy is unstable. Skilled personnel are hard to find. All of this constrains predictive modelling capabilities (Adeyemi & Adebayo, 2024).

So there is a gap. A big one. The academic literature talks about advanced techniques. The Zimbabwean insurance sector operates in a very different reality. What is needed are context-appropriate, rule-based NLP solutions (Li et al., 2023; Zhang et al., 2022).

**2.5 Natural Language Processing in Risk Assessment**

What exactly is NLP? It is a subfield of AI focused on getting machines to understand human language. In risk assessment, NLP provides tools for turning unstructured text into structured representations that models can use (Kumar, Singh & Sharma, 2023).

The theoretical foundation is feature extraction. You convert text into numerical features that capture syntactic and semantic information (Hassan et al., 2022).

Here is a key contribution. NLP can identify latent risk indicators. These are implicit signals hidden inside textual narratives. They are invisible to structured data models. Descriptions of hazardous road conditions, driver distraction, or sudden manoeuvres provide valuable risk insights. NLP can systematically quantify them (Zhang et al., 2022).

But effectiveness depends on data quality and methodological choices. Advanced machine learning models offer high performance, but they need large datasets and significant computing power. Rule-based NLP approaches are different. They are simpler and more interpretable. They use explicitly defined linguistic rules, which makes their decision-making transparent and easy to audit. That is a big advantage in regulated industries (Hassan et al., 2022; Adeyemi & Adebayo, 2024).

**2.6 Review of NLP Techniques for Risk Extraction**

Let me walk you through the main NLP techniques used for risk extraction.

**2.6.1 Tokenisation and Preprocessing**

Tokenisation is the first step. You break text into smaller units like words or phrases. It sounds simple, but it is not. Accident reports are often written under time pressure. They contain spelling errors and informal language. Robust tokenisation needs error correction and domain-specific vocabulary handling (Li et al., 2023; Kumar et al., 2023).

**2.6.2 Keyword Extraction**

TF-IDF is a common technique. It stands for Term Frequency-Inverse Document Frequency. It identifies significant terms by assigning weights based on how often they appear. The problem? These methods often miss contextual relationships. The word "speeding" might mean different things depending on whether it was the primary cause or just a background condition. Hybrid approaches that combine keyword extraction with contextual analysis work better (Cheng et al., 2022; Zhang et al., 2022).

**2.6.3 Rule-Based NLP Systems**

Rule-based systems rely on predefined linguistic rules. They encode domain expertise into explicit if-then rules. In motor insurance, rule-based approaches can identify risk indicators like "drunk driving," "overspeeding," and "poor visibility." Their transparency is a major advantage. You can see exactly why they made a decision. That matters for regulatory compliance. Plus, you can refine them incrementally without retraining the whole model (Hassan et al., 2022; Verbelen et al., 2021).

Are rule-based systems less flexible than machine learning? Yes. But here is the thing. In resource-constrained environments like Zimbabwe, flexibility is not the priority. Practicality is. Rule-based systems deliver interpretable risk assessments without needing extensive computational infrastructure. That makes them a pragmatic choice (Adeyemi & Adebayo, 2024).

**2.7 Six-Dimension Risk Model Architecture**

Recent advancements have formalised what I call a vertically integrated AI paradigm for motor insurance. It unifies perception, reasoning, and production infrastructure. Panboonyuen (2026) presents domain-adapted transformer architectures that process multimodal data for comprehensive risk assessment.

Within this paradigm, risk is operationalised through six dimensions. Let me break them down.

**Behavioural Dimension** gets a 35% weight. It captures driver actions like speeding, drunk driving, distraction, and fatigue. NLP analysis extracts these from accident narratives using keywords and rule patterns.

**Environmental Dimension** gets a 10% weight. It includes weather conditions like rain and fog, road surface quality, lighting, and visibility. Most of this comes from unstructured text descriptions.

**Temporal or Time Dimension** gets a 10% weight. It covers time of day, day of week, seasonal patterns, and holiday periods. This combines structured data with narrative context.

**Vehicle Dimension** gets a 15% weight. It encompasses vehicle age, type, engine capacity, value, and mechanical condition. A mix of structured fields and textual notes on defects.

**Location Dimension** gets a 10% weight. It includes geographic risk factors like urban or rural classification, specific high-risk intersections, and regional accident density. Structured postcodes combine with placename extraction from narratives.

**Claims and Severity Dimension** gets a 20% weight. It covers historical claims frequency, prior accident severity, injury indicators, and property damage extent. A blend of structured claims history and textual severity descriptions.

Here is how it all fits together. A structured underwriting index derived from age, vehicle type, and prior claims is combined with dimension-specific rule-based factor scores from textual analysis. This blended scoring approach produces more accurate and nuanced risk classification than either method alone (Hatzesberger & Nonneman, 2026; Zhang et al., 2022).

**2.8 Knowledge Base Integration and Term Prevalence**

Here is an innovation I find particularly interesting. Knowledge base integration.

A knowledge base is a repository of historical accident narratives. It stores aggregate statistics on term prevalence and risk patterns. When an applicant submits location or descriptive text, NLP analysis extracts phrases and matches them against a gazetteer. That is just a predefined list of risk-relevant terms.

The knowledge base then provides calibration lifts. If a term appears frequently in historical accident files, the corresponding risk dimension score gets adjusted upward (Hassan et al., 2022; Kumar et al., 2023).

Why does this matter? It moves away from purely static rule systems. The system can adjust dynamically based on local data patterns. And you do not need full machine learning retraining to do it. For developing contexts where labelled training data is scarce, knowledge base-calibrated rule systems offer an accessible path to better predictive accuracy (Adeyemi & Adebayo, 2024; Li et al., 2023).

**2.9 Applications and Advantages of NLP in Insurance**

NLP is not just theoretical. It is being used across insurance.

Claims processing. Fraud detection. Customer service automation. Underwriting. In motor insurance, combining structured and unstructured data provides more comprehensive risk understanding. That leads to improved pricing strategies (Cheng et al., 2022; Kumar et al., 2023).

A report from Intellias (2025) documents how NLP-powered systems can analyse broker submissions, adjuster reports, and inspection files. They extract risk-relevant details that would otherwise stay buried in unstructured documents.

What are the advantages? Improved accuracy, for starters. Models capture contextual information that structured data alone cannot see. Efficiency is another one. Automation reduces manual effort and processing time. Scalability matters too. You can process thousands of documents rapidly (Hatzesberger & Nonneman, 2026; Hassan et al., 2022).

For Zimbabwe, rule-based NLP systems offer a cost-effective way to leverage existing textual data without needing extensive computational resources (Adeyemi & Adebayo, 2024).

**2.10 Research Gap**

Now let me be clear about what is missing in the literature. There are several gaps, and my study tries to address them.

**First gap.** There is limited research on motor insurance risk assessment using accident narratives. Most studies focus on structured data models. They have not fully explored the informational content of textual accident reports in the insurance pricing process, especially in developing countries (Verbelen et al., 2021; Backlund & Ohman, 2023).

**Second gap.** There is a lack of focus on developing countries like Zimbabwe. Existing studies come from well-resourced insurance markets in North America, Europe, and East Asia. Their findings might not translate directly to Zimbabwe. Data quality is different. Linguistic variability is different. Infrastructure is different (Adeyemi & Adebayo, 2024; The Financial Gazette, 2026).

**Third gap.** There is an over-reliance on complex machine learning models. Deep learning approaches dominate the literature. The potential of simpler, rule-based NLP systems has been left relatively unexplored. That is a problem for resource-constrained settings where simple and practical is better (Hassan et al., 2022; Li et al., 2023).

**Fourth gap.** There is limited exploration of six-dimension blended scoring with knowledge base calibration. Multidimensional risk frameworks have been proposed. But there is not much empirical research on implementing them using rule-based NLP and knowledge base term prevalence for local market adaptation (Panboonyuen, 2026; Zhang et al., 2022).

So here is what my study does. It proposes a rule-based NLP approach for extracting risk indicators across six dimensions from motor insurance accident narratives. It integrates these with structured data through blended scoring. It calibrates predictions using a knowledge base of historical accident term prevalence specifically for the Zimbabwean context. Finally, it evaluates the feasibility and effectiveness of this approach. The evidence will be directly relevant to practitioners and policymakers in developing insurance markets (Adeyemi & Adebayo, 2024; Cheng et al., 2022).

**2.11 Chapter Summary**

Let me wrap up what this chapter has covered.

I reviewed the literature on motor insurance risk assessment and NLP applications. Traditional actuarial models provide a valuable foundation, but their reliance on structured data leaves significant informational gaps. NLP techniques, particularly rule-based systems, offer a transparent and interpretable way to extract risk indicators from accident narratives.

The six dimensions are Behavioural, Environmental, Temporal, Vehicle, Location, and Claims. Each plays a role.

I also looked at the Zimbabwean context. Data fragmentation, economic instability, and limited technological infrastructure are real challenges. But there are positive signs too. The Insurance Council of Zimbabwe is launching emergency response initiatives. Telematics adoption is growing. The readiness for data-driven innovation is increasing.

The chapter established a clear rationale for my study. Develop a rule-based NLP approach. Integrate it with a knowledge base for term prevalence calibration. Tailor it to the resource constraints and specific risk patterns of the Zimbabwean motor insurance market. That is exactly what I set out to do.

**CHAPTER 3: RESEARCH METHODOLOGY**

**3.0 Introduction**

This chapter presents the research methodology used in the development of the Motor Insurance Policyholder Risk Profiling System using Natural Language Processing (NLP) and rule-based risk scoring techniques. The chapter explains the research design, requirements analysis, system development approach, tools and technologies used, data collection methods, implementation process, and system workflow. Furthermore, the chapter describes the architecture of the system and explains how different components interact to produce policyholder risk assessments. The methodology adopted in this research aims to provide an efficient, scalable, and explainable solution for motor insurance risk evaluation (Cheng, Liu & Wang, 2022; Hassan, Bashir & Mahmood, 2022).

**3.1 Research Design**

The research employed an experimental and prototype-based research design to develop and evaluate a motor insurance risk assessment system. The study focused on integrating Natural Language Processing (NLP), rule-based scoring techniques, and knowledge-base analysis to assess the likelihood of future insurance claims (Verbelen, Antonio & Claeskens, 2021).

The experimental approach was selected because it allows continuous testing, refinement, and evaluation of the developed system under different policyholder scenarios. The system was developed iteratively, enabling improvements to be made after each testing phase. The prototype development model was adopted because it supports gradual refinement of system features based on performance evaluation and user requirements (Boodhun & Jayabalan, 2018).

The research combined structured data analysis with NLP-assisted text analysis. Structured data such as driver age, vehicle type, prior claims, annual mileage, and driving behaviour were analyzed using predefined underwriting rules. Additionally, NLP techniques were used to analyze place names and keywords associated with accident-prone areas using a gazette-based matching system (Li, Xu & Zhao, 2023).

The study also incorporated a knowledge-base component consisting of accident report text files. These files were analyzed to identify common risk-related patterns, location frequencies, and environmental indicators that influence motor insurance risk (Kumar, Singh & Sharma, 2023).

The overall research design enabled the development of a rule-based insurance risk engine, integration of NLP for keyword and location analysis, construction of a knowledge-base calibration system, continuous testing and refinement of risk-scoring rules, and generation of explainable and interpretable insurance risk predictions (Panboonyuen, 2026; Zhang, Chen & Li, 2022).

**3.1.1 Requirements Analysis**

Requirements analysis was conducted to identify the functional and non-functional requirements necessary for the successful development of the motor insurance risk profiling system. The analysis focused on determining system capabilities, operational constraints, user expectations, and technical resources required for implementation (Adeyemi & Adebayo, 2024).

**3.1.1.1 Functional Requirements**

Functional requirements describe the operations and services that the system must perform (Hassan et al., 2022).

**Table 3.1: Functional Requirements**

|     |     |
| --- | --- |
| **Requirement** | **Description** |
| Policyholder Risk Assessment | The system shall calculate motor insurance risk scores for policyholders. |
| Structured Data Processing | The system shall process form-based policyholder information such as age, claims history, and vehicle details. |
| NLP Keyword Analysis | The system shall analyze place names and keywords using Natural Language Processing techniques. |
| Risk Classification | The system shall classify policyholders into Low, Medium, High, Very High, or Critical risk categories. |
| Knowledge Base Analysis | The system shall analyze accident report text files to identify frequently occurring risk indicators. |
| Risk Explanation Generation | The system shall generate decision traces explaining how risk scores were calculated. |
| API Communication | The system shall allow communication between the frontend and backend using REST APIs. |
| Data Storage | The system shall store accident corpus statistics using SQLite databases. |

**3.1.1.3 Hardware Requirements**

**Table 3.3: Hardware Requirements**

|     |     |
| --- | --- |
| **Hardware Component** | **Specification** |
| Processor | Intel Core i5 or higher |
| RAM | 8 GB minimum |
| Storage | 500 GB HDD/SSD |
| Network | Internet connectivity for development and testing |

**3.1.1.4 Software Requirements**

**Table 3.4: Software Requirements**

|     |     |
| --- | --- |
| **Software** | **Purpose** |
| Python | Backend development and risk scoring |
| FastAPI | REST API development |
| React | Frontend user interface |
| SQLite | Knowledge base database storage |
| spaCy | Natural Language Processing |
| Visual Studio Code | Development environment |
| Git | Version control |
| npm | Frontend package management |

**3.2 System Development**

The development of the Motor Insurance Policyholder Risk Profiling System followed a prototype-based software development methodology. The system was developed incrementally through several stages including frontend development, backend API implementation, NLP integration, rule-based scoring development, knowledge-base implementation, and testing (Hatzesberger & Nonneman, 2026).

The frontend was developed using React to provide an interactive step-by-step form interface for policyholders. The backend was implemented using FastAPI to handle API requests, scoring calculations, NLP processing, and communication with the knowledge base (Intellias, 2025).

The scoring engine was designed to combine structured underwriting factors, rule-based risk indicators, NLP keyword analysis, and knowledge-base calibration (Cheng et al., 2022; Zhang et al., 2022). The system was continuously tested using different policyholder scenarios to evaluate scoring accuracy, response time, and overall system functionality (Poufinas et al., 2023).

**3.2.1 System Development Tools**

Several tools and technologies were used during system development (Kumar et al., 2023).

Python

Python was selected as the primary programming language because of its simplicity, flexibility, and extensive support for data processing and NLP applications. Python also provides rich libraries that support backend API development and rule-based systems (Hassan et al., 2022).

FastAPI

FastAPI was used to develop RESTful API endpoints for communication between the frontend and backend. It was selected because of its high performance, asynchronous processing capabilities, and ease of integration with Python-based systems (Li et al., 2023).

React

React was used to build the frontend user interface. It provided a responsive and interactive multi-step form system for collecting policyholder information (NewsDay, 2025).

SQLite

SQLite was used as the local database management system for storing knowledge-base statistics, accident report metadata, and NLP analysis results (The Financial Gazette, 2026).

spaCy

spaCy was used to implement Natural Language Processing functionalities such as phrase matching, entity recognition, and gazette-based keyword extraction (Panboonyuen, 2026).

Visual Studio Code

Visual Studio Code was used as the Integrated Development Environment (IDE) for coding, debugging, and project management (Backlund & Ohman, 2023).

**3.2.2 Prototype Model**

The prototype software development model was adopted for this research because it supports iterative system refinement and continuous testing. The system was first developed as a basic prototype containing core risk-scoring functionalities. Additional features such as NLP processing, knowledge-base calibration, and explanation generation were added progressively (Verbelen et al., 2021).

The prototype model allowed early testing of scoring algorithms, validation of system workflows, continuous improvement of risk rules, and easier identification of system weaknesses during development (Adeyemi & Adebayo, 2024; Boodhun & Jayabalan, 2018).

**3.3 System Design**

The system was designed using a multi-layer architecture consisting of the frontend layer, backend API layer, NLP processing layer, scoring engine, and knowledge base (Panboonyuen, 2026).

The frontend layer collects policyholder information through a step-by-step form. The backend API receives the submitted data and coordinates the scoring and NLP processes. The NLP layer analyzes place names and keywords while the scoring engine calculates risk scores across multiple dimensions. The knowledge base adjusts scores using statistics derived from accident report corpora (Zhang et al., 2022).

**3.3.1 Data Flow Diagram**

**Table 3.5: Main Data Flow Components**

|     |     |
| --- | --- |
| **Component** | **Function** |
| User | Inputs policyholder information |
| Frontend Interface | Collects and sends form data |
| Backend API | Processes incoming requests |
| NLP Engine | Performs keyword and gazette analysis |
| Risk Engine | Calculates risk scores |
| Knowledge Base | Provides statistical calibration |
| Database | Stores accident statistics and NLP outputs |
| Results Interface | Displays risk scores and explanations |

**3.3.2 Proposed System Flowchart**

System Flow Description

The system follows a sequential workflow. After the user submits policyholder details through the frontend, the backend validates the input, calculates a structured underwriting score, and performs NLP analysis on placename text. Risk dimension scores are then calculated, adjusted by the knowledge base, and combined into a composite score. Finally, the system classifies the

risk and returns the results with an explanation trace.

**3.4 Dataset and Knowledge Base**

The system utilizes a knowledge-base dataset consisting of accident report text files and gazette datasets. The accident reports are stored as text documents and analyzed to identify commonly occurring risk indicators, locations, and accident-related keywords (Kumar et al., 2023).

The gazette dataset contains insurance-related phrases, labels, and categories used for NLP phrase matching and entity recognition (Li et al., 2023).

**3.4.1 Gazette Dataset**

The gazette dataset contains structured phrase mappings used by the NLP engine (Hassan et al., 2022).

**Table 3.6: Gazette Dataset Structure**

|     |     |
| --- | --- |
| **Field** | **Description** |
| Phrase | Keyword or phrase to detect |
| Label | Assigned NLP label |
| Category | Associated risk category |

**3.4.2 Knowledge Base Dataset**

The knowledge base stores accident report files, keyword frequencies, category statistics, and location prevalence information (The Financial Gazette, 2026; Adeyemi & Adebayo, 2024). The knowledge base supports score calibration by increasing or decreasing dimension scores based on historical accident trends (Hatzesberger & Nonneman, 2026).3.5 Data Collection Methods

Observation was used as the primary data collection method during system testing and evaluation. Multiple policyholder scenarios were entered into the system and the generated outputs were observed and analyzed (Verbelen et al., 2021).

The researcher evaluated (Cheng et al., 2022; Poufinas et al., 2023):

- scoring accuracy
- response time
- NLP keyword detection
- risk classification consistency
- system stability

Accident report text files were also collected and analyzed to build the knowledge base used for NLP calibration (NewsDay, 2025; The Financial Gazette, 2026).

**3.6 Implementation**

System implementation involved integrating all frontend, backend, NLP, and database components into a unified application (Intellias, 2025).

The frontend was implemented using React and communicates with the backend through HTTP API requests. The backend API processes policyholder information, calculates structured scores, performs NLP analysis, and generates final risk classifications (Panboonyuen, 2026).

The NLP engine processes location-related text using spaCy EntityRuler and gazette matching. The scoring engine calculates six risk dimensions: Behavioural Risk, Environmental Risk, Time Risk, Vehicle Risk, Location Risk, and Claims Severity Risk (Zhang et al., 2022; Hatzesberger & Nonneman, 2026). The knowledge base adjusts scores based on accident frequency statistics and keyword prevalence (Kumar et al., 2023; Li et al., 2023).

**3.7 Summary of How the System Works**

The Motor Insurance Policyholder Risk Profiling System operates through a multi-stage process designed to assess the likelihood of future insurance claims. Initially, the user enters policyholder information through a frontend form interface. The submitted information is transmitted to the backend API for processing (Cheng et al., 2022).

The backend calculates a structured underwriting score using demographic and vehicle-related factors. Simultaneously, the NLP engine analyzes place names and location keywords using gazette matching techniques. Rule-based scoring algorithms then calculate risk scores across six dimensions (Hassan et al., 2022).

The knowledge base further adjusts the scores using statistical information obtained from previously analyzed accident reports. A final composite risk score is generated and classified into predefined risk levels such as Low, Medium, High, Very High, or Critical (Verbelen et al., 2021).

Finally, the system generates a detailed explanation trace showing the factors that contributed to the final decision (Zhang et al., 2022).

**3.8 Testing and Evaluation**

The system underwent several testing procedures to evaluate functionality, reliability, and accuracy (Boodhun & Jayabalan, 2018; Poufinas et al., 2023).

Table 3.7: Testing Procedures

|     |     |
| --- | --- |
| **Testing Type** | **Purpose** |
| Unit Testing | Testing individual modules independently |
| API Testing | Verifying backend API functionality |
| Integration Testing | Ensuring frontend and backend compatibility |
| NLP Testing | Evaluating keyword detection accuracy |
| Usability Testing | Assessing user interaction and interface simplicity |
| Performance Testing | Measuring response time and system stability |

**3.9 General Overview of the Application**

The application is designed to assist insurance organizations in evaluating policyholder risk using structured data analysis and NLP-enhanced risk profiling. The system combines traditional underwriting factors with rule-based and knowledge-base approaches to improve decision-making (Adeyemi & Adebayo, 2024; Intellias, 2025).

The system provides automated risk scoring, risk classification, explainable decision traces, and accident-pattern analysis (Hatzesberger & Nonneman, 2026; Kumar et al., 2023). The application supports both insurance assessors and researchers by providing a scalable and interpretable risk assessment framework (Panboonyuen, 2026).

**3.10 Summary**

This chapter presented the research methodology used in the development of the Motor Insurance Policyholder Risk Profiling System. The chapter discussed the research design, requirements analysis, development methodology, system architecture, datasets, implementation techniques, and testing procedures (Verbelen et al., 2021; Cheng et al., 2022).

The prototype development model enabled iterative system improvement while the integration of NLP and rule-based scoring enhanced the accuracy and interpretability of policyholder risk assessments. The system combines structured underwriting analysis with knowledge-base calibration to generate reliable and explainable insurance risk predictions (Hassan et al., 2022; Zhang et al., 2022).