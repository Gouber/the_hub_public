# The Idea

The hub was a project aimed at giving back the power to the renter (specifically students). By building
a state-of-the-art managing platform combined with a built-in review system, landlords would be
able to manage their property from the click of a button and renters would be guaranteed a voice
when landlords don't respect their obligations. The idea was to restore the balance in a market where 
the renter had little power and where students were heavily affected - a typical student
does not have the money to engage in a legal battle with a landlord.

# Tech Used

Undertaking this project has been a steep learning curve of technologies I'd never used before.
Here is a breakdown of the technologies used, the challenges that came with them and what I've
managed to learn throughout this process:

### Django

I never used Django before tackling this project, and my understanding of python syntax was 
minimal. I had to go through the initial tutorials on Django with the Python documentation opened. Often, I'd 
struggle to understand snippets of code as both my Django and my Python were not very good. However,
I learnt by writing code - I had to go through several iterations of the same functionality until
I was able to do things both the Django but as well as the pythonic way. Here are some highlights worth mentioning:

* **Custom Login backend** - I wanted my app to allow for login to be performed via the email as opposed
to the username. I also wanted the rich admin functionality that Django offered to remain intact - This meant
I couldn't simply rename username to email and consider this task done . I had to research the Django way
and this lead me to write a custom backend that uses the email. Writing a custom backend was also
incredibly useful when I decided to port the frontend to React and use JWT tokens to login. Because of this
custom backend approach I only had to plug in the JWT based approach as opposed to rewriting the entire logic (saving a lot of time).

* **Extending the admin functionality** - The logic was that a django-model called `Lease` would hold
a `House` and several `CustomUser`. The `admin` app was not able to generate a form where a `Lease`
could hold several `CustomUser`. I had to research how to extend the functionality as I was only able
to do this task from the command line (which would prove annoying for debugging but also, not feasible in the future when we'd have
support not familiar with Django handling issues through the admin website). This
exention can be seen [here](https://github.com/Gouber/the_hub_public/blob/main/hub/houses_hub/admin.py).

* **Porting to Django-rest** - Modern web apps are responsive and dynamic. I wanted this project
to follow suit and decided to implement the frontend in React. This meant rewriting the entire logic
in a microservice-based approach. This meant modifying code that looked like 
[this](https://github.com/Gouber/the_hub_public/blob/214eea7832587ded5496aaf0c3830cd1e79e6797/hub/login_register_service_hub/views.py#L43) (code still there for the purpose of this readme)
to the microservice-based approach in [here](https://github.com/Gouber/the_hub_public/blob/214eea7832587ded5496aaf0c3830cd1e79e6797/hub/houses_hub/views.py#L33) - note 
this shows code for different logic (because the `simple-jwt` package comes with built-in functions - see [here](https://github.com/Gouber/the_hub_public/blob/214eea7832587ded5496aaf0c3830cd1e79e6797/hub/login_register_service_hub/urls.py#L35))

For more examples of my applied knowledge of Django please browse this repository - you'll find elegant solutions 
backed by rigorous testing to problems ranging from optimizing data-flow to addressing security concerns.  

### React

I had no React experience in the past. My Javascript level was beginner at best and I never worked 
with Typescript either. I took the challenge of writing a frontend in React (and later to replace Javascript with Typescript) because I like new challenges 
and I'm always eager to learn technology that I don't know. Here are some highlights

* Integrating `formik` to make testing, refactoring and reasoning about forms much more efficient. 
From the very beginning, I noticed out-of-the-box forms in React are really verbose with
no special functionality offered to the developer. I researched modern solutions and having come across
`formik` I realised this package will save time, improve readability and make overall developer life much easier.
I adopted `formik` and replaced the simpler [registration](https://github.com/Gouber/the_hub_public/blob/main/hub_frontend/src/Components/login_register_service_hub/forms/RegisterForm.tsx) and [login](https://github.com/Gouber/the_hub_public/blob/main/hub_frontend/src/Components/login_register_service_hub/forms/LoginForm.tsx) forms.
The main challenge was adopting the `formik` mindset with the more dynamic [apply](https://github.com/Gouber/the_hub_public/blob/main/hub_frontend/src/Components/login_register_service_hub/forms/DynamicApplyForm.tsx) form - 
this is because the `apply` form had to support a variable number of fields depending on how many students
would apply to a specific house.

* Integrating `react-router` was essential as I wanted visitors to be able to navigate backwards and forwards.

* Creating an instant chat system
    * I wanted the messages to appear on the screen right after they are sent - I had to make use of `socket.io` broadcast functionality
    * I had to make use of
    `socket.io` to provide a chat feature that was able to separate messages into groups (separating connections in different [rooms](https://socket.io/docs/rooms/)) -
    as a student might have different chats with different people
    * I wanted to refresh the JWT token in real time to not force the user to log back in if he's active in a chat. 
    The JWT token would expire after 5 minutes but if a student is active (sending messages through the app) then
    he shouldn't have to log back in after 5 minutes - the app should be smart enough to refresh the token (I made use of
    refresh tokens here)
    * I wrote a simple express [app](https://github.com/Gouber/the_hub_public/blob/main/hub_frontend/src/ChatApp/Server/index.js) to act as the intermediary server in-between my frontend and backend 
    and facilitate the functionality above.

* I had to extend the [google-maps-react](https://www.npmjs.com/package/google-maps-react) package with extra
functionality such that I could have deeper access to the vertices on the screen - the extension I wrote can be found in [google-maps-react-delete-vertices](https://www.npmjs.com/package/google-maps-react-delete-vertices).
The problem was that the `google-maps-react` package didn't offer a way to get the most updated state of the vertices
on the screen (when rendering a Polygon). I needed access to the most updated state as I wanted to let users refine
their search for properties by drawing on the screen the area they are interested in. This task was particulary interesting 
as I had to dive deep into the React ecosystem and research where such code should be added such that React can still have the 
expected level of control over this component - such as to not break the rest of the functionality. 


By further browsing the repository you should also see elegant React code that truly compartmentalizes
functionality in its logical parts.  



# Conclusion

Tackling such a project taught me a great deal about planning & researching. I had to carefully plan the models and the views 
so as to allow for the complex relations one would expect from a bigger project. The code was written
with the idea that it will be extended and hence code re-usability and concepts such as DRY 
have been carefully considered. I had to perform a lot of research into areas of tech I haven't used before. This taught me where
and how to look for solutions to problems. Furthermore, this project taught me how to develop code
in languages/frameworks that I've never used before - specifically by being very considerate of the opinionated-approach frameworks give
as accepting the slightly steeper curve for the way frameworks want you to implement code gives massive returns
when you want to further extend your project. Please feel free to reach back to me if you have any further questions.
