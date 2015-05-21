#!/bin/sh

JFDIR="../.."
TARGET="template_jobflow_ci_config_app.yaml"
TMPL="$JFDIR/templates/template_jobflow_ci_config_base.yaml"
VALUES="values_jobflow_app.yaml"

echo $*

if [ $# -gt 0 ]; then
    VALUES=$1
fi
if [ $# -gt 1 ]; then
    TARGET=$2
fi

python $JFDIR/render_jobflow_templates.py --template $TMPL --values $VALUES > $TARGET
echo "Input template: $TMPL"
echo "Input values  : $VALUES"
echo "Output stored : $TARGET"

