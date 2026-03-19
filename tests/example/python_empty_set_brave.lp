set_declare(test,my_set).
{ set_assign(test,my_set,val(str,"A")) }.

evaluate(python("len"),(variable(my_set),())).

#show evaluated/3.