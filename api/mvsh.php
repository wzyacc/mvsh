<?php
require 'vendor/autoload.php';

use Elasticsearch\ClientBuilder;

$host = ["hosts"=>"http://192.168.31.104:9200"];

$client = ClientBuilder::create()->setHosts($host)->build();

$q = $_GET["q"];

$sq = "";
for($i=0;$i<strlen($q);$i++){
   $sq .= $q[$i]." ";
}

$params = [
    'index' => 'yse8',
    'type' => 'mv_records',
    'body' => [
        'query' => [
            'match_phrase' => [
                'name_pinyin' => $sq
            ]
        ]
    ]
];

$response = $client->search($params);
//print_r($response);

$data = Array();
foreach($response["hits"]["hits"] as $rd){
	$sc = $rd["_source"];
	$rd = Array("name" => $sc["name"],"mv_img"=>$sc["mv_img"],"mv_real_plist"=>$sc["mv_real_plist"]);
	array_push($data,$rd);
}
$ret = Array("code"=>200,"data"=>$data);

echo json_encode($ret);

?>
