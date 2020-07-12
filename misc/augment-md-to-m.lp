% - Augmentation of an Md domain instance with destination objects for compatiblity with M ----
%
%  - augmemts destination objects with corresponding related orders, products and shelves
%  - run as
%
%       $ clingo augment-md-to-m.lp your-instance.lp --out-ifs='\n' -V0 --out-atomf='%s.' | head -n -1
%
%    to get an equivalent instance in M format


init(object(order,D),  value(line,(D,1));
     object(product,D),value(on,(D,1));
     object(shelf,D),  value(at,C))      :- init(object(destination,D),value(at,C)).
