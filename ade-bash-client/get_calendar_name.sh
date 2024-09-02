export GWT=AB00CDEA

if [ -z ${COOKIE+x} ]; then
  echo "COOKIE is unset"; 
  exit
fi

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <query_calendar_id>"
  exit
fi

curl -s 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/ConfigurationServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|8|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|0513C80A56E7DA3488A651BBD7D3690F|com.adesoft.gwt.core.client.rpc.ConfigurationServiceProxy|method42getToolTipParticipant|J|I|java.lang.String/2004016611|{\"13\"\"true\"[4]{\"StringField\"\"NAME\"\"\$LabelName\"\"\"\"false\"\"false\"{\"StringField\"\"WEB_RESOURCE\"\"\$LabelWebResource\"\"\"\"false\"\"false\"{\"StringField\"\"CODE_RESOURCE\"\"\$column.CodeResource\"\"\"\"false\"\"false\"{\"StringField\"\"CAPACITY\"\"LabelCapacity\"\"\"\"false\"\"false\"|1|2|3|4|3|5|6|7|$GWT|$1|8|" | sed "s/\"NAME\",\"\([^\"]*\)\"/\nNAME=\1\n/g" | sed -n "s/NAME=\(.*\)/\1/p"
