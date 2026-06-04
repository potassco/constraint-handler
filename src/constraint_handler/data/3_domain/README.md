### Input predicates

\_expression(sugar,val/2).
\_expression(sugar,operation/2).
\_passed(sugar,LBL,variable_define/2).
\_passed(sugar,LBL,variable_domain/2).
\_passed(sugar,LBL,variable_declare/2).
\_passed(sugar,LBL,set_assign/2).
\_passed(sugar,LBL,set_baseDomain/2).

### Intermediate predicates

\_expression_tupleLength/3.
\_expression_tupleIndex/4.
\_expression_domain/2.
\_expression_tupleDomainAux/3.
\_expression_setDomainQuery/2.
\_expression_setExpr/4.
\_expression_setExprIndex/5.
\_expression_setDomain/4.

### Output predicates

None.
