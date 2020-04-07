INFORMATION FOR MODEL USERS

-> add content


INFORMATION FOR CONTRIBUTERS

Coding conventions TBP Corona_Model project

1. Everybody is welcome to contribute. 
    To keep track of peoples' contributions, please add your name to the list of authors at the top of each file in the Corona_Model repository 
    if you have contributed to the file itself (code, text, data, figures, etc.) or to collecting the data contained therein/used for it.
2. Start variable names with small letters, class and function names with capital letters.
3. Please comment on your code. 
    This is a community project and others have to understand what you are doing without having to ask you all the time. To distinguish real 
    comments from out-commented code start all your comments with ##.
4. Python has no type declarations. 
    To avoid confusion between developers, please add a type indicator to your variable names, e.g., for a counter of type int use the name 
    counter_int, for a dict of age groups use ageGroup_dict. This allows everyone at every time (even in some years) to immediately know what 
    type of information is stored in a certain variable. Together with descriptive variable names this significantly improves readability of code.
5. Use getter/setter. 
    Applying getter/setter policies avoids allocation problems (compare 3.)  and eases logging and debugging.
6. Use unittest. 
    We want to keep the model expandable, presumably opening the depository to the public. The bigger it will grow the more difficult to keep the 
    overview about different dependencies. A test suite allows to maintain functionality when including new features.
7. Constructive criticism is appreciated. 
    If you find a possibility to improve existing material (code, text, data, figures, etc.), please contact the author(s) of the respective 
    material and discuss your suggestions. Find consensus if possible or seek for further advice from the rest of the team.
8. Use gitlab repository issues to organize work. 
    Please either assign the issues directly to specific people, e.g., a question with respect to the data to the person collecting it, or keep 
    track of closing them once solved.
