# Meet Joe
This is Leo & Thomas's amazing science fair project.

We're making a project that aims to create a more organized, more accessible, system for machine learning training & tracking.
The machine learning system that we're using will be based off of Andrej Karpathy's (@karpathy) char-rnn project (github.com/karpathy/char-rnn), 
which is designed to analyze & emulate text at the character level using recurrent neural networks.
I (Thomas) have had a bit of experience with RNNs before, but I'm certainly no ML expert.

This will also tie into my (Thomas's) IDS project, as we will be using relational databases to track information about the users, datasets, models, loss, learning rates, iterations, etc.

This project will be powered largely with open-sourced free software such as: 
*Apache2 (our web server),
*Flask (our web framework),
*MariaDB (our DBMS),
*PyTorch (the deep learning system behind the AI),
*and many other smaller things like flask-mail, flask-login, flask-mysql, mysql-connector/python, w3.css, and so on.

It is currently being run on ON A BRAND NEW X570 CUSTOM MADE COMPUTER LETSS GOoo, available in development at http://99.199.44.233, although no guarantees that it's gonna be online.




**How can we create a website that makes interacting with neural networks accessible and easy?**

## **Background Research**

Neural networks are complicated tools that are extremely precise and unique. Due to the advanced and somewhat random training process of neural networks, altering one tiny variable might completely affect the performance of the network. To allow users to alter these variables, we must create a relational database which stores the values the users gave from the website. Connecting the database to the neural network will apply the choices the user made to the network, flawlessly linking them together. The database will also store the datasets which the users are able to upload. These datasets will be used to train neural networks, and users will be able to upload anything from tweets to wikipedia articles. The database is also crucial to receiving user feedback, as it stores the user accounts, passwords, and most importantly, email address. In order for us to receive feedback on user experience and suggestions on how to improve, we need to send users a survey to the email address the user provided. This is where a server is needed. We can use a server called Flask to render our website, allowing us to host a web server with Apache2 on our own IP address. Flask also has the capability to send emails, making it possible for us to contact users for further feedback. Finally, we have the website templates. User experience is greatly affected by how professional and clean a website looks, so using a framework such as w3.css will make designing the aesthetic part of the website much more convenient. This also makes it easier to add elements into the website such as a navigation bar and slide show, not just adding more convenience in the user experience, but also more fun.

Variables such as the number of neurons in a hidden layer, or the number of hidden layers, greatly affect the structure and performance of the neural network. Users are able to change these variables through Joe (our website).


## **Abstract**

Joe is a project designed to make utilizing neural networks not just simple and quick, but also fun and accessible. Using and interacting with neural networks and machine learning in general is widely considered a daunting and scary task to those without a computer science background. Yet as machine learning becomes further integrated into an essential part of industries and economies, there still isn’t a very convenient and simple method for people to interact with these increasingly relevant technologies. The importance of making neural networks less scary and more exciting was not lost upon us, and we came up with a solution: designing a website that connects user and artificial intelligence seamlessly. By creating a platform where users are able to upload data sets, create their own neural networks, and generate text from artificial intelligence, we have pushed neural networks one step closer to becoming more user friendly and accessible. We hope that because of our project, using neural networks will no longer be challenging and arduous, and that anyone, disregarding previous computer science knowledge, will be able to experience the joy of teaching a computer.



**Procedure**

Testing process:


*   New users create an account which contains their email address so we can contact them in the future, and to mitigate the chance of spamming or mal use of our website. 
*   Designing a survey with 10 questions as follows: 
1. On a scale of 1 to 10, how comfortable are you with computers and technology in general? 
1. On a scale of 1 to 10, how confusing did you find navigating the website? 
1. On a scale of 1 to 10, how hard/confusing was uploading a dataset? 
1. On a scale of 1 to 10, how hard/confusing was creating a model for you? 
1. On a scale of 1 to 10, how hard/confusing was generating text from the models? 
1. On a scale of 1 to 10, how clear were the descriptions and explanations on the website? If possible, please list the confusing ones. 
1. Did you enjoy your experience on our website? If not, state why. 
1. What improvements do you suggest to make using our website more simple? 
*   Users were able to give additional input, giving suggestions or comments on areas of the website that were not specifically asked about. 
*   After users had uploaded a dataset, created a model, and generated text, an email will be sent to them asking them to complete the survey.
*   All of the feedback will be stored and recorded in our database where they will be analyzed and changes to the website will be made.

Note: During the testing of our website, we experienced a problem regarding the survey. It turns out that many users who created accounts did not receive the survey because they didn’t complete all the tasks required. This led us to having 20 accounts created on our website, but only 2 survey responses. To solve this problem we added the following revision to our procedure:



*   To ensure that all users of our website can provide feedback, the link to the survey will also be sent to those who have not completed the tasks required. Questions about tasks that the users have not done will be supplemented with a link with the area of the website associated with the task. For example, if a user has not created a model, they can click a link on the survey which sends them to the model maker page.


## **Initial Prototype**

	Joe consists of three major components. The server, the database, and the actual neural network. We decided to run an **Apache2 **web server connected via **mod_wsgi** to our main server using the **Flask **microframework. Flask is excellent for its easy customization and scalability. Used with other modules such as **WTForms**, which is used for rendering, validating, and processing forms, Flask allow users to input information. **Flask_mail** allows us to securely send automated mail such as email verifications, notifications, and survey requests through the Gmail server. **Flask_login** keeps track of where users are logged in, and **MySQL Connector/Python** connects us to our MariaDB database. Python’s famous flexibility and overall straightforward environment lets us easily harness and connect all of these systems for our site.

**MariaDB** is based off the MySQL **relational database system**, and it allows us to track everything that happens on our site. It consists of several tables, which track important assets and their properties such as users, datasets, models, checkpoints, votes, and our survey. This is basically the deeply hidden glue that holds everything together. User inputted variables such as the number of hidden layers, are also sent and stored in the database. These then connect to the neural networks.

We used **PyTorch** for all of our work with neural networks. PyTorch is a powerful framework which provides most necessary machine learning features. A large portion of our code managing the RNNs is based off of **[github.com/thundercomb/pytorch-char-rnn/](https://github.com/thundercomb/pytorch-char-rnn/)**, a PyTorch implementation of Andrej Karpathy’s original **Char RNN** project. This system uses **gated recurrent units**, a new type of RNN based off of older, less efficient LSTMs. Although GRUs struggle more with long term memory (which LSTMs were originally designed for), the time it takes to train is certainly worth it. These models are trained on a NVidia GTX 1660 Ti graphics card using **CUDA**, a computation system for NVidia GPUs. This is effective because graphics processing units have a significant advantage over traditional CPUs for the repetitive floating-point operations that occur in machine learning.

To properly present these things to the user, we need a website template. Utilizing a framework called w3 css, we significantly simplified the process of editing and improving the aesthetics of our website. To make our website more friendly to those inexperienced with machine learning and computer science we gave our website and our whole project a nickname: Joe. This friendly, familiar name is seen throughout the website, and we hope it reduces some of the daunting nature of training neural networks.  We also made a navigation bar on the top of the website so that users can access all parts of the website quickly and easily. We also added some explanations and descriptions for the technical portions of our project.


## **Future Work**

The world of neural networks is constantly evolving and developing. Hundreds of different neural networks structures, types, and purposes already exist today, and thousands more will be developed in the future. Our innovation is somewhat limited in that it only connects users to Gated Recurrent Units (GRUs) neural networks which only generate text. In the future, we would like to diversify the type of neural networks we use as well as their purpose. Different neural networks have different advantages and purposes. Using a Long short term memory (LSTM) neural network for instance, would improve the quality of the generated text but take longer to train. Our innovation also has the potential of completing totally different tasks, for example, using a convolutional neural network for analyzing photos. Due to the increased size of our project we would like to potentially migrate to another larger framework, **Django**, which more directly connects the server to other important parts such as a database. Some parts of our project were also limited by our computing ability. If we had a more professional high-end processor, we would be able to train larger models and more models faster, although CUDA has probably sped up our computation over 50x than what it would it would be on our CPU.


## **Background**

	The roots of the project began with a YouTube video by _carykh _on rap lyrics generated by a neural network. This idea of training neural networks to generate text greatly intrigued Thomas, and he downloaded the code to try it out himself. Yet as he ran the code on his own computer, he was perplexed by the complexities of uploading a data-set, creating a model, and setting the dozens of variables required to create a neural network. Furthermore, the program had to be run through a terminal with extremely complicated commands, making the already difficult task even less appealing. Thus the idea of our project was inspired. Christened with the name of Joe, it would make training neural networks simple and fun, allowing anyone, regardless of previous knowledge and experience to generate text from machine learning models.


## **Purpose**

To many, just hearing the words “neural network”, “machine learning”, or “artificial intelligence” seems foreign and confusing.  These concepts, although potentially interesting to some, seem unattainably advanced, impossibly conceptual, and simply befuddling. Joe is here to change that. Using Joe, users can interact and generate text from neural networks from anywhere, anytime. Still providing freedom to the user, Joe streamlines the process of uploading data sets, creating neural network models, and generating text, making neural networks not just fascinating concept, but a fun real-life tool.




## **Error Analysis**

Although the innovative nature of our project reduces the number of potential errors in our data (after all, user errors are part of improving our website), there are still errors that could have occurred which might have affected the data we have collected.



*   The formatting of the questions in the survey could have been interpreted differently by different people, so the results collected might be inaccurate.
*   During updates to the site, users may experience “internal server error”, which could have drastically affected user experience. During times when our server (Thomas’ computer) was down, the website was also simply inaccesible.
*   Changes to the website were still being added as new users joined, so user experience may have different for newer users. For example, variables controlling the model were not described in most stages of our site. Some users were hindered by bugs in the site that were in effect while they were using it, such as the page tracking the model’s progress freezing.
*   Despite reaching out to many people, twenty created accounts, only six of which ended up submitting a survey. This made it very difficult for us to draw conclusions about what improvements were required.

## **Discussion**

	Although the sample size of our feedback was limiting, we still received some very interesting results. Over time, users seemed to have a slightly less difficult time on the website (see Fig. 1) , as the average of the last three survey responses was 19.333, lower than the average of the first three survey responses, which was 26. This tells us the updates and improvements we were making did make a difference in user experience. The user’s level of comfort with technology did not seem to be correlated to their general experience, which indicates that problems with the site were not necessarily associated with lack of experience using websites. Interestingly, as the overall score of 18 show, users found generating text to be the most simple and straightforward process. Yet users found uploading datasets and creating new models significantly harder, the first scoring 26 and the second scoring 31, even though the process of doing all three of those activities was very similar. We believe that this was because of the overwhelming number of choices users were given on pages meant for uploading datasets and creating models. In order to still provide users who have more experience with machine learning more options, we could implement two modes, one with significantly less fields to fill and more detailed descriptions than the models. Generating models, on the other hand, had significantly fewer fields that required user input, which likely was the factor behind its much higher ease of use. Uploading models however, were not the most complex part of our website. At an overall score of 41, navigating the website proved to be the most difficult. This could be because of the structuring of the website, as users had to follow a certain path to reach parts of the website, instead of getting instantly sent to their desired destination. By implementing elements on our navigation bar such as a dropdown which gives links to all parts of the website, we could potentially make navigating the website much simpler. 

Although it is much harder to graphically represent, these scores were not the only user input we received. Users were also able to give suggestions through text, and there was a common theme throughout all of the input we received. Many of the users felt the use of terminology and jargon on the website was confusing, and that the descriptions we provided were still insufficient. To solve this, we have applied popups to the labels of fields users needed to fill out. When users hover their mouse over the label, a description would popup with a more detailed explanation providing more information about the field. Another way for us to improve the quality of our explanations would be to add a glossary page with definitions of terminologies and technical language commonly used.



## **Acknowledgements**



*   Thank you to David Einstein for funding our graphics card, the GTX 1660 Ti mentioned earlier, for computing neural networks. Training models would have 50 times slower if even possible without the graphics card.
*   All participants who have used our site, especially Alpha teachers and minischool parents. The feedback and suggestions given by the participants were invaluable to the project.
*   Thank you to Mrs Moore, whose passion, enthusiasm, and dedication have made this science fair journey so much easier. Her advice and guidance has saved us many hours of stress.
