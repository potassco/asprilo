#!/usr/bin/env bash
# = Converts M domain instance to Md domain format ==============================================

CLINGO=${CLINGO:-'clingo'}
MODE=M2MD
ENCSPDIR="$(dirname "$(realpath "$0")")"

if [ -v CONVENC ]; then
    INSTANCE=$1
    INFO="M/Md Instance converted via custom encoding $CONVENC"
 else
     INSTANCE=$2
     case "$1" in
         --m2md)
             ENC_BASENAME="convert-m-to-md.lp"
             INFO="M-domain instance converted to domain Md"
             ;;
         --md2m)
             ENC_BASENAME="convert-md-to-m.lp"
             INFO="Md-domain instance converted to domain M"
             ;;
         --am2md)
             ENC_BASENAME="augment-m-to-md.lp"
             INFO="M-domain instance augmented for domain Md"
             ;;
         --amd2m)
             ENC_BASENAME="augment-md-to-m.lp"
             INFO="M-domain instance augmented for domain Md"
             ;;
         *)
             cat <<-EOF
		Usage: convert-md.sh --m2md|--md2m|--am2md|--amd2m INSTANCE_FILE
		  --m2md:  M to Md conversion
		  --md2m:  Md to M conversion
		  --am2md: M to Md augmentation
		  --amd2m: Md to M augmentation
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
