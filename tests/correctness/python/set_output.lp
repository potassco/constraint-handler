variable_define(pool,operation(python("lambda: {1, 3}"),())).
variable_define(size,operation(length,(variable(pool),()))).
variable_define(has_three,operation(python("lambda pool: 3 in pool"),(variable(pool),()))).

#show value/2.
#show set_value/2.
