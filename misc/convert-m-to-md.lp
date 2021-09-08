% - Rewrite an M domain instance to an equivlant Md instance ------------------------------------
%
%  - replaces related orders, products and shelves with corresponding destination objects
%  - run as
%
%       $ clingo convert-m-to-md.lp your-instance.lp --out-ifs='\n' -V0 --out-atomf='%s.' | head -n -1
%
%    to get an equivalent instance in Md format

#show.
#show init(object(destination,D), value(at,C)) : init(object(order,D),  value(line,(A,_))),
                                                 init(object(product,A),value(on,(S,_))),
                                                 init(object(shelf,S),  value(at,C)).
#show init(object(O,T),           value(A,V))  : init(object(O,T),      value(A,V)), {O=product;
                                                                                      O=order;
                                                                                      O=shelf;
                                                                                      O=pickingStation
                                                                                     } = 0.
