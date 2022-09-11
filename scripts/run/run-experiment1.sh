#!/bin/bash
#
# Runs Testar experiment 1
# 
# Settings
# 1. Protocol: should be webdriver_ckan1
PROTOCOL=webdriver_ckan1
# 2. Condition (experimental, control-defaultactionselection, control-customactionselection)
CONDITION=experimental
# 3. Experiment name
EXPNAME="test1808"
# 4. Main data directory
MAINDATADIR="/data/studie/af/output"
# 5. NumberOfSequences
NUMSEQUENCES=2
# 6. Sequence length (number actions in sequence)
SEQUENCELENGTH=10
# 7. Number first run
FIRSTRUN=1
# 8. Number last run >= first run
LASTRUN=2
# 9. OrientDB settings
ORIENTDB_DIR="/opt/orientdb"
ORIENTDB_USER="root"
ORIENTDB_PASSWORD="testar"
ORIENTDB_CONNECTDB="demodb"
ORIENTDB_TESTARDB="testar"

# --- end of settings

set -x

# Create data main directory if it doesn't exist
if ! [ -d "$MAINDATADIR" ]
then mkdir -p "$MAINDATADIR"
fi

GLOBAL_OPTIONS="sse=$PROTOCOL ShowVisualSettingsDialogOnStartup=false Mode=Generate Sequences=$NUMSEQUENCES SequenceLength=$SEQUENCELENGTH"

# Look up options for experimental condition

if [ "$CONDITION" == "experimental" ]
then EXP_OPTIONS="Expcondition=experimental SetLogContext=true SetCoverageContext=true ProcessDataAfterAction=true CompoundTextActionLogicEnabled=true DockerComposeDirectory=/data/studie/af/lightweight-codeanalysis/suts/ckan/run CarryOverCoverage=true StateModelEnabled=true ExportCoverage=true"
elif [ "$CONDITION" == "plain" ]
then EXP_OPTIONS="ExpCondition=control-defaultactionselection SetLogContext=false SetCoverageContext=false ProcessDataAfterAction=false CompoundTextActionLogicEnabled=false DockerComposeDirectory=/data/studie/af/lightweight-codeanalysis/suts/ckan_plain/run CarryOverCoverage=false StateModelEnabled=false ExportCoverage=false"
elif [ "$CONDITION" == "control-defaultactionselection" ]
then EXP_OPTIONS="ExpCondition=control-defaultactionselection SetLogContext=false SetCoverageContext=true ProcessDataAfterAction=false CompoundTextActionLogicEnabled=false DockerComposeDirectory=/data/studie/af/lightweight-codeanalysis/suts/ckan/run CarryOverCoverage=true StateModelEnabled=true ExportCoverage=true"
elif [ "$CONDITION" == "control-customactionselection" ]
then EXP_OPTIONS="ExpCondition=control-customactionselection SetLogContext=false  SetCoverageContext=true ProcessDataAfterAction=false CompoundTextActionLogicEnabled=true DockerComposeDirectory=/data/studie/af/lightweight-codeanalysis/suts/ckan/run CarryOverCoverage=true StateModelEnabled=true ExportCoverage=true"
else echo "Error: unknown experimental condition $CONDITION" && exit 1
fi

for RUN in $(seq "$FIRSTRUN" "$LASTRUN")
do  DATADIR="$MAINDATADIR/$EXPNAME.$CONDITION.$RUN"
    LOGCONTEXTPREFIX="$EXPNAME.$CONDITION.$RUN"
    RUN_OPTIONS="CoverageExportDirectory=$DATADIR OutputDir=$DATADIR LogContextPrefix=$LOGCONTEXTPREFIX"
    ORIENTDB_EXPORTFILE="$DATADIR/statedb.dump"

    # Create data directory
    mkdir "$DATADIR"

    # Write settings file
    cat > "$DATADIR/exp1.settings" << SETTINGSFILE
    Experiment    : $EXPNAME
    Condition     : $CONDITION
    Run           : $RUN
    Global options: $GLOBAL_OPTIONS
    Run options   : $RUN_OPTIONS
SETTINGSFILE

    ## Create state database
    if [ "$CONDITION" != "plain" ]
    then
    $ORIENTDB_DIR/bin/console.sh "CONNECT remote:localhost/$ORIENTDB_CONNECTDB $ORIENTDB_USER $ORIENTDB_PASSWORD; CREATE DATABASE remote:localhost/$ORIENTDB_TESTARDB $ORIENTDB_USER $ORIENTDB_PASSWORD;"
    fi

    ## Run experiment
    cd  /data/studie/af/TESTAR_dev/testar/target/install/testar/bin || exit 1
    ./testar $GLOBAL_OPTIONS $EXP_OPTIONS $RUN_OPTIONS >& "$DATADIR/experiment.log"

    ## Export state database
    if [ "$CONDITION" != "plain" ]
    then
    $ORIENTDB_DIR/bin/console.sh "CONNECT remote:localhost/$ORIENTDB_TESTARDB $ORIENTDB_USER $ORIENTDB_PASSWORD; EXPORT DATABASE $ORIENTDB_EXPORTFILE;"
    fi

    ## Drop state database
    if [ "$CONDITION" != "plain" ]
    then
    $ORIENTDB_DIR/bin/console.sh "CONNECT remote:localhost/$ORIENTDB_CONNECTDB $ORIENTDB_USER $ORIENTDB_PASSWORD; DROP DATABASE remote:localhost/$ORIENTDB_TESTARDB $ORIENTDB_USER $ORIENTDB_PASSWORD"
    fi
done

echo "Run script done."
