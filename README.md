This is a web application built using React. I begin with trying to take data from Solcast using their API and passing it as a CSV file. My intention was to have C++ perform calculations on the data and then pass it to Python. After about two weeks, I found that this approach prresented too many obstacles and, in a way, I was over-complicating the whole process.

I decided to keep everything in Python for the backend. I then Moved away from Solcast and breifly flirted with the NASA API but again, I came up againsts problems parsing the JSON data.

Finbally, I settled on NERL. Their API worked much better. Additional obstacles I emcountered ove the six week project window were mostly issues with porting the application to AWS. I tried Elastic Beanstalk and found problems that would not be solved in time. I finally found luck with AWS Amplify. 


I use python3 on the backend to take solar irradiance data from NERL and construct a graph and table.
The sliders can be adjusted in real time to control the calculations for both the graph and table. 

The application (both front and back) are hosted on AWS.
