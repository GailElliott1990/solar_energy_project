This web application was built using React for the frontend and Python for the backend. Before starting this project, I had never developed an application before, and my limited experience meant I spent a lot of time searching online for solutions to Python errors and seeking guidance from other programmers.

Initially, I attempted to integrate data from the Solcast API and export it as a CSV file. The plan was to use C++ for calculations and then pass the results back into Python. Solcast are very strict with API calls so I tried to incorporate Redis Server to cache the data. After roughly two weeks, however, I realized this approach introduced unnecessary complexity and obstacles.

I decided to streamline the process by keeping the entire backend in Python. After briefly experimenting with the NASA API and running into challenges parsing JSON data, I finally settled on using the NREL API, which proved to be much more manageable.

Over the course of the seven-week development window, I encountered additional hurdles, mainly related to deploying the application on AWS. Elastic Beanstalk presented issues I couldn’t resolve within the project’s timeframe, but AWS Amplify ultimately offered a suitable solution.

The final product fetches solar irradiance data from the NREL API, and the Python backend generates both a graph and a data table for the user. Interactive sliders on the frontend allow for real-time adjustments to the calculations displayed in the graph and table. Both the frontend and backend are hosted on AWS.
