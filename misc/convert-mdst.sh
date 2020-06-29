#!/usr/bin/env bash
# = Converts M domain instance to M-dst domain format ==============================================

CLINGO=${CLINGO:-'clingo'}
MODE=M2MDST
ENCSPDIR="$(dirname "$(realpath "$0")")"

if [ -v CONVENC ]; then
    INSTANCE=$1
    INFO="M/M-dst Instance converted via custom encoding $CONVENC"
 else
     INSTANCE=$2
     case "$1" in
         --m2mdst)
             ENC_BASENAME="convert-m-to-mdst.lp"
             INFO="M-domain instance converted to domain M-dst"
             ;;
         --mdst2m)
             ENC_BASENAME="convert-mdst-to-m.lp"
             INFO="M-dst-domain instance converted to domain M"
             ;;
         --am2mdst)
             ENC_BASENAME="augment-m-to-mdst.lp"
             INFO="M-domain instance augmented for domain M-dst"
             ;;
         --am2mdst)
             ENC_BASENAME="augment-mdst-to-m.lp"
             INFO="M-domain instance augmented for domain M-dst"
             ;;
         *)
             cat <<-EOF
		Usage: convert-mdst.sh --m2md|--md2m|--am2md INSTANCE_FILE
		  --mdst:  M to M-dst conversion
		  --m2mdst:  M-dst to M conversion
		  --am2mdst: M to M-dst augmentation
		  --amdst2m: M-dst to M augmentation
		EOF
             exit
             ;;
     esac
fi

CONVENC=${CONVENC:-"$ENCSPDIR/$ENC_BASENAME"}

HEADER=\
"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\
%
% $INFO with:\n\
%   - conversion encoding: $CONVENC\n\
%   - input instance: $INSTANCE\n\
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"

TRANSCRIPT=$(
    echo -e "$HEADER"
    sed '/% init/q'<$INSTANCE
    $CLINGO\
        --out-ifs='\n' -V0 --out-atomf='%s.'\
        $CONVENC $INSTANCE | \
        head -n -1
          )

echo -e "$TRANSCRIPT"
