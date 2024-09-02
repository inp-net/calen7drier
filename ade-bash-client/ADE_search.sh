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

curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/MyPlanningClientServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|8|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|217140C31DF67EF6BA02D106930F5725|com.adesoft.gwt.directplan.client.rpc.MyPlanningClientServiceProxy|method1login|J|com.adesoft.gwt.core.client.rpc.data.LoginRequest/3705388826|com.adesoft.gwt.directplan.client.rpc.data.DirectLoginRequest/635437471||1|2|3|4|2|5|6|$GWT|7|0|0|0|1|1|8|8|-1|0|0|" -o /dev/null
#curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/DirectPlanningServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|9|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|067818807965393FC5DCF6AECC2CA8EC|com.adesoft.gwt.directplan.client.rpc.DirectPlanningServiceProxy|method1login|J|com.adesoft.gwt.core.client.rpc.data.LoginRequest/3705388826|Z|com.adesoft.gwt.directplan.client.rpc.data.DirectLoginRequest/635437471||1|2|3|4|3|5|6|7|$GWT|8|0|9|0|1|1|9|9|-1|0|0|0|" -o /dev/null

curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/DirectPlanningServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|7|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|067818807965393FC5DCF6AECC2CA8EC|com.adesoft.gwt.directplan.client.rpc.DirectPlanningServiceProxy|method13loadProject|J|I|Z|1|2|3|4|3|5|6|7|$GWT|$PROJECT_ID|1|" -o /dev/null

curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/DirectPlanningServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|7|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|067818807965393FC5DCF6AECC2CA8EC|com.adesoft.gwt.directplan.client.rpc.DirectPlanningServiceProxy|method12searchResource|J|java.lang.String/2004016611|[1]{\"StringField\"\"NAME\"\"\"\"$1\"\"false\"\"true\"\"true\"\"true\"\"2147483647\"\"false\"[0]\"CONTAINS\"\"false\"\"false\"\"0\"|1|2|3|4|2|5|6|$GWT|7|" | tr -d '\\' | sed "s/{\"\([0-9]*\)\"\"false\"/\nRESULTAT=\1\n/g" | sed -rn "s/RESULTAT=(.*)/\1/p"
