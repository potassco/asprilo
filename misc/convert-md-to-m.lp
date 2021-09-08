% - Rewrite an Md domain instance to an equivlant M instance ------------------------------------
%
%  - replaces destination objects with corresponding related orders, products and shelves
%  - run as
%
%       $ clingo convert-md-to-m.lp your-instance.lp --out-ifs='\n' -V0 --out-atomf='%s.' | head -n -1
%
%    to get an equivalent instance in M format

#show.
#show init(object(order,D),  value(line,(D,1));
           object(product,D),value(on,(D,1));
           object(shelf,D),  value(at,C))      : init(object(destination,D),value(at,C)).
#show init(object(O,T),      value(A,V))       : init(object(O,T),          value(A,V)), {O=product;
                                                                                          O=order;
                                                                                          O=shelf;
                                                                                          O=pickingStation;
                                                                                          O=dest
                                                                                         } = 0.
