export GWT=AB00CDEA

if [ -z ${COOKIE+x} ]; then
  echo "COOKIE is unset"; 
  exit
fi

if [ "$#" -ne 0 ]; then
  echo "this script takes no argument"
  exit
fi

curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/MyPlanningClientServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|8|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|217140C31DF67EF6BA02D106930F5725|com.adesoft.gwt.directplan.client.rpc.MyPlanningClientServiceProxy|method1login|J|com.adesoft.gwt.core.client.rpc.data.LoginRequest/3705388826|com.adesoft.gwt.directplan.client.rpc.data.DirectLoginRequest/635437471||1|2|3|4|2|5|6|$GWT|7|0|0|0|1|1|8|8|-1|0|0|" -o /dev/null
#curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/DirectPlanningServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|9|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|067818807965393FC5DCF6AECC2CA8EC|com.adesoft.gwt.directplan.client.rpc.DirectPlanningServiceProxy|method1login|J|com.adesoft.gwt.core.client.rpc.data.LoginRequest/3705388826|Z|com.adesoft.gwt.directplan.client.rpc.data.DirectLoginRequest/635437471||1|2|3|4|3|5|6|7|$GWT|8|0|9|0|1|1|9|9|-1|0|0|0|" -o /dev/null

curl 'https://edt.inp-toulouse.fr/direct/gwtdirectplanning/WebClientServiceProxy' -X POST -H 'Content-Type: text/x-gwt-rpc; charset=utf-8' -H 'X-GWT-Permutation: a' -H 'X-GWT-Module-Base: https://edt.inp-toulouse.fr/direct/gwtdirectplanning/' -H 'Origin: https://edt.inp-toulouse.fr' -H "Cookie: JSESSIONID=$COOKIE" --data-raw "7|0|5|https://edt.inp-toulouse.fr/direct/gwtdirectplanning/|34BFB581389200AE2C2012C5A7E57F95|com.adesoft.gwt.core.client.rpc.WebClientServiceProxy|method4getProjectList|J|1|2|3|4|1|5|$GWT|"
