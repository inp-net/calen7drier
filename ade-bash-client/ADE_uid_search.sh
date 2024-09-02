#!/usr/bin/env bash
export GWT=AB00CDEA
export PROJECT_ID=67 # N7 2024-2025

if [ -z ${COOKIE+x} ]; then
  echo "COOKIE is unset"; 
  exit
fi

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <query_string>"
  exit
fi

# connect to service and enable the GWT (used in all other queries)
curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/MyPlanningClientServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|8|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|217140C31DF67EF6BA02D106930F5725|com.adesoft.gwt.directplan.client.rpc.MyPlanningClientServiceProxy|method1login|J|com.adesoft.gwt.core.client.rpc.data.LoginRequest/3705388826|com.adesoft.gwt.directplan.client.rpc.data.DirectLoginRequest/635437471||1|2|3|4|2|5|6|$GWT|7|0|0|0|1|1|8|8|-1|0|0|" -o /dev/null
#curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/DirectPlanningServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|9|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|067818807965393FC5DCF6AECC2CA8EC|com.adesoft.gwt.directplan.client.rpc.DirectPlanningServiceProxy|method1login|J|com.adesoft.gwt.core.client.rpc.data.LoginRequest/3705388826|Z|com.adesoft.gwt.directplan.client.rpc.data.DirectLoginRequest/635437471||1|2|3|4|3|5|6|7|$GWT|8|0|9|0|1|1|9|9|-1|0|0|0|" -o /dev/null

# load the project (N7 or other Toulouse-INP school ADE for specific school year)
curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/DirectPlanningServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|7|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|067818807965393FC5DCF6AECC2CA8EC|com.adesoft.gwt.directplan.client.rpc.DirectPlanningServiceProxy|method13loadProject|J|I|Z|1|2|3|4|3|5|6|7|$GWT|$PROJECT_ID|1|" -o /dev/null

# select a random id in the list of advance search presets (in n7 ade, we cannot add more presets but can edit. In ENSAT ade, we can add more presets but cannot edit "name" preset)
export ADVANCE_SEARCH_ID=$(curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/ConfigurationServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|10|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|0513C80A56E7DA3488A651BBD7D3690F|com.adesoft.gwt.core.client.rpc.ConfigurationServiceProxy|method15getFilterConfiguration|J|com.adesoft.gwt.core.client.rpc.config.FilterType/1396315430|java.lang.String/2004016611|Z|[0]|{\"0\"\"50\"\"NAME\"\"true\"|1|2|3|4|6|5|6|7|8|8|7|$GWT|6|0|9|0|0|10|" | tr -d '\\' | sed "s/{\"\([0-9]*\)\"\"/\nRESULTAT=\1\n/g" | sed -rn "s/RESULTAT=(.*)/\1/p" | tail -n 1) # tail -n 1 select last preset in alphanumeric order, may fail (see previous comment)

# modify the preset to select user that perfectly match specific uid
curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/ConfigurationServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|7|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|0513C80A56E7DA3488A651BBD7D3690F|com.adesoft.gwt.core.client.rpc.ConfigurationServiceProxy|method20updateFilterConfiguration|J|java.lang.String/2004016611|{\"$ADVANCE_SEARCH_ID\"\"zmyuid\"\"-1\"\"all\"\"true\"\"edtall\"\"-2\"\"SEARCH_RESOURCE\"[1][1]{\"StringField\"\"CODEX_RESOURCE\"\"column.CodeXResource\"\"$\"\"false\"\"true\"\"true\"\"true\"\"2147483647\"\"false\"[0]\"SAME_AS\"\"false\"\"false\"\"0\"[0]\"0\"\"true\"[0]|1|2|3|4|2|5|6|$GWT|7|" -o /dev/null

# search using the modified preset
curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/ConfigurationServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|10|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|0513C80A56E7DA3488A651BBD7D3690F|com.adesoft.gwt.core.client.rpc.ConfigurationServiceProxy|method17applySearchConfiguration|J|java.lang.String/2004016611|java.util.List|{\"$ADVANCE_SEARCH_ID\"\"zmyuid\"\"-1\"\"all\"\"true\"\"edtall\"\"-2\"\"SEARCH_RESOURCE\"[1][1]{\"StringField\"\"CODEX_RESOURCE\"\"column.CodeXResource\"\"$1\"\"false\"\"true\"\"true\"\"true\"\"2147483647\"\"true\"[0]\"SAME_AS\"\"false\"\"false\"\"0\"[1]\"$1\"\"0\"\"true\"[0]|java.util.ArrayList/4159755760|java.lang.Integer/3438268394|1|2|3|4|4|5|6|7|7|$GWT|8|9|1|10|5571|9|0|" | tr -d '\\' | sed "s/{\"\([0-9]*\)\"\"false\"/\nRESULTAT=\1\n/g" | sed -rn "s/RESULTAT=(.*)/\1/p"
