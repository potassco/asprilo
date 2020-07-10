% - Augmentation of an M domain instance with dest(ination) objects for compatiblity with Md ----
%
%   - augments related orders, products and shelves with corresponding dest(ination) objects
%   - run as
%
%        $ clingo augment-m-to-md.lp your-instance.lp --out-ifs='\n' -V0 --out-atomf='%s.' | head -n -1
%
%     to get an equivalent instance in Md format

init(object(dest,D), value(at,C)) :- init(object(order,D),  value(line,(A,_))),
                                     init(object(product,A),value(on,(S,_))),
                                     init(object(shelf,S),  value(at,C)).
