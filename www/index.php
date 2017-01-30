<?
if(isset($_POST['pw'])) {
	setCookie('pw',$_POST['pw']);
	$_COOKIE['pw'] = $_POST['pw'];
}
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Midas</title>
	</head>
	<body>
		<h1>Midas</h1>
<?
include('config.php');
if(!isset($_COOKIE['pw']) || $_COOKIE['pw'] != $pw){
	$action = 'pw';
}else{
	echo '<nav>
		<a href="/">Wichtiges</a>
		<a href="/?a=artlist">Sch&uuml;ttgut</a>
		<a href="/?a=artnew">Neuer Artikel</a>
		<a href="/?a=prepaid">Guthaben</a>
	</nav>';
	if(isset($_GET['a'])){
		$action = $_GET['a'];
	}else{
		$action = 'index';
	}
}

$file_db = new PDO('sqlite:data.db');
$file_db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
setlocale(LC_MONETARY, 'de_DE');

function chk($str,$allow=false) {
	$return = str_replace("'", "`", $str);
	$return = str_replace('"', "`", $return);
	if(!$allow)
		$return = str_replace(strtolower('<script'),'&lt;script',$return);
	return $return;
}

function chkP($str) {
	$return = str_replace("..", "", $str);
	$return = str_replace('./', "", $return);
	return $return;
}

function chkA($str) {
	$erlaubt = array('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9','-','_');
	$l = strlen($str);
	$r = '';
	for($i=0;$i<$l;$i++) {
		if(in_array($str{$i},$erlaubt))
			$r .= $str{$i};
	}
	return $r;
}

function chkN($str){
	if(is_numeric($str))
		return (int)$str;
	else
		return false;
}

if($action == 'pw') {
	echo '<form action="" method="post">
	Passwort: <input name="pw" type="password" />
	<input type="submit" value="Einloggen" />
	</form>';
}

// Füllmengen unter dem Softlimit
//fertig
if($action == 'index'){
	//Daten die unterhalb des softlimits sind
	$result = $file_db->query('SELECT * FROM snacks WHERE amount <= softlimit');
	echo '<table><tr><th>EAN</th><th>Name</th><th>Preis</th><th>Amount(SL)</th></tr>';
	foreach($result as $res) {
		echo '<tr><td>'. $res['snackID'] .'</td><td>'. $res['name'] .'</td>
		<td>'. money_format('%.2i', $res['price']) .' Euro</td>
		<td>'. $res['amount'] .'('. $res['softlimit'] .')</td><td>
			[<a href="/?a=artedit&id='. $res['snackID'] .'">edit</a>]
		</td></tr>';
	}	
	echo '</table>';
}

// Artikel editieren
if($action == 'artedit') {
	$id = chkA($_GET['id']);
	if(isset($_POST['submit'])) {
		$name = chk($_POST['name']);
		$softlimit = chkN($_POST['softlimit']);
		$preis = chkN(str_replace(',','.',$_POST['price']))*100;
		
		$sth = $file_db->prepare('UPDATE snacks SET name = :name ,price = :price, softlimit = :softlimit WHERE snackID = :id');
		if($sth->execute(array(':name'=>$name, ':softlimit'=>$softlimit, ':price'=>$preis, ':id'=>$id))) {
			echo 'Eintrag ge&auml;ndert.<br/>';
		}else{
			echo '&Auml;nderung fehlgeschlagen.<br/>';
		}
		$action = 'artlist';
	}else{
		$result = $file_db->query("SELECT * FROM snacks WHERE snackID = '{$id}' LIMIT 1");
		$ok = false;
		foreach($result as $res) {
			$ok = true;
			$preis = str_replace('.',',',$res['price']);
			echo '<form action="/?a='. $action .'&id='. $_GET['id'] .'" method="post">
				<table>
					<tr><td>EAN</td><td>'. chkA($_GET['id']) .'</td></tr>
					<tr><td>Name</td><td>
						<input type="text" name="name" value="'. $res['name'] .'" />
					</td></tr>
					<tr><td>Preis</td><td>
						<input type="text" name="price" value="'. $preis .'" />
					</td></tr>
					<tr><td>Softlimit</td><td>
						<input type="text" name="softlimit" value="'. $res['softlimit']/100 .'" />
					</td></tr>
					<tr><td><input type="submit" name="submit" value="Speichern" /></td></tr>
			</form>';
		}
		
		if(!$ok) {
			echo 'Eintrag existiert nicht.<br/>';
			$action = 'artlist';
		}
	}
}

// Neuen Artikel eintragen
if($action == 'artnew') {
	if(isset($_POST['submit'])) {
		$name = chk($_POST['name']);
		$softlimit = chkN($_POST['softlimit']);
		$preis = chkN(str_replace(',','.',$_POST['price']))*100;
		
		$sth = $file_db->prepare('UPDATE snacks SET name = :name ,price = :price, softlimit = :softlimit WHERE snackID = :id');
		if($sth->execute(array(':name'=>$name, ':softlimit'=>$softlimit, ':price'=>$preis, ':id'=>$id))) {
			echo 'Eintrag ge&auml;ndert.<br/>';
		}else{
			echo '&Auml;nderung fehlgeschlagen.<br/>';
		}
		$action = 'artlist';
	}else{
		$result = $file_db->query("SELECT * FROM ucos ORDER BY tstmp DESC LIMIT 10");
		echo '<form action="/?a='. $action .'" method="post">
			<table>
				<tr><td>EAN</td><td><select name="snackID">';
		foreach($result as $res) {
			echo '<option value="'. $res['ucoID'] .'">'. $res['ucoID'] .' ('. $res['tstmp'] .')</option>';
		}
		echo '</select></td></tr>
				<tr><td>Name</td><td>
					<input type="text" name="name" value="" />
				</td></tr>
				<tr><td>Preis</td><td>
					<input type="text" name="price" value="" />
				</td></tr>
				<tr><td>Softlimit</td><td>
					<input type="text" name="softlimit" value="" />
				</td></tr>
				<tr><td><input type="submit" name="submit" value="Speichern" /></td></tr>
		</form>';
	}
}

if($action == 'artinv') {
	$id = chkA($_GET['id']);
	if(isset($_POST['submit'])) {
		$amount = chk($_POST['amount']);
		if($_POST['rel'] == 1) {
			$sth = $file_db->prepare('UPDATE snacks SET amount = amount + :amount WHERE snackID = :id');
		}else{
			$sth = $file_db->prepare('UPDATE snacks SET amount = :amount WHERE snackID = :id');
		}
		
		if($sth->execute(array(':amount'=>$amount, ':id'=>$id))) {
			echo 'Eintrag ge&auml;ndert.<br/>';
		}else{
			echo '&Auml;nderung fehlgeschlagen.<br/>';
		}
		$action = 'index';
	}else{
		$result = $file_db->query("SELECT * FROM snacks WHERE snackID = '{$id}' LIMIT 1");

		$ok = false;
		foreach($result as $res) {
			$ok = true;
			echo '<form action="/?a='. $action .'&id='. $id .'" method="post">
				<h2>'. $res['name'] .'['. $res['snackID'] .']</h2>
				<select name="rel"><option value="1">rel</option><option value="0">abs</option></select>
				<input type="text" name="amount" value="0" />
				<input type="submit" name="submit" value="Verrechnen" />
			</form>';
		}
		
		if(!$ok) {
			echo 'Eintrag nicht gefunden';
			$sction = 'index';
		}
	}
}

// Alle Artikel
//fertig
if($action == 'artlist') {
	if(isset($_POST['search']))
		$s = chkA($_POST['search']);
	else
		$s = '';
	
	echo '<form action="/?a=artlist" method="post">
		<input type="text" name="search" value="'. $s .'" />
		<input type="submit" name="submit" value="Suchen" />
	</form>';
	
	
	$result = $file_db->query("SELECT * FROM snacks WHERE name LIKE '%{$s}%' OR snackID LIKE '%{$s}%'");

	echo '<table><tr><th>EAN</th><th>Name</th><th></th><th>Amount(SL)</th></tr>';
	foreach($result as $res) {
		echo '<tr><td>'. $res['snackID'] .'</td><td>'. $res['name'] .'</td>
		<td>'. money_format('%=*^-14#8.2i', $res['price']/100) .' Euro</td>
		<td>'. $res['amount'] .'('. $res['softlimit'] .')</td><td>
			[<a href="/?a=artedit&id='. $res['snackID'] .'">Edit</a>]
			[<a href="/?a=artinv&id='. $res['snackID'] .'">Inventur</a>]
		</td></tr>';
	}	
	echo '</table>';
}

if($action == 'preedit') {
	$id = chkA($_GET['id']);
	if(isset($_POST['submit'])) {
		$info = chk($_POST['info']);
		$cash = chkN(str_replace(',','.', $_POST['cash'])*100);
		$saldo = chkN(str_replace(',','.', $_POST['saldo'])*100);
	
		$sth = $file_db->prepare('UPDATE tokens SET info = :info ,cash = :cash, saldo = :saldo WHERE tokenID = :id');
		if($sth->execute(array(':info'=>$info, ':cash'=>$cash, ':saldo'=>$saldo, ':id'=>$id))) {
			echo 'Eintrag ge&auml;ndert.<br/>';
		}else{
			echo '&Auml;nderung fehlgeschlagen.<br/>';
		}
		$action = 'prepaid';
	}else{
		$result = $file_db->query("SELECT * FROM tokens WHERE tokenID = '{$id}' LIMIT 1");
		$ok = false;
		foreach($result as $res) {
			$ok = true;
			$cash = str_replace('.',',',$res['cash']/100);
			$saldo = str_replace('.',',',$res['saldo']/100);
			echo '<form action="/?a='. $action .'&id='. $_GET['id'] .'" method="post">
				<table>
					<tr><td>UUID</td><td>'. chkA($_GET['id']) .'</td></tr>
					<tr><td>Info</td><td>
						<input type="text" name="info" value="'. $res['info'] .'" />
					</td></tr>
					<tr><td>Guthaben</td><td>
						<input type="text" name="cash" value="'. $cash .'" />
					</td></tr>
					<tr><td>Kredit</td><td>
						<input type="text" name="saldo" value="'. $saldo .'" />
					</td></tr>
					<tr><td><input type="submit" name="submit" value="Speichern" /></td></tr>
			</form>';
		}
		
		if(!$ok) {
			echo 'Eintrag existiert nicht.<br/>';
			$action = 'prepaid';
		}
	}
}

// Alle Guthaben
if($action == 'prepaid') {
	if(isset($_POST['search']))
		$s = chkA($_POST['search']);
	else
		$s = '';
	
	echo '<form action="/?a=prepaid" method="post">
		<input type="text" name="search" value="'. $s .'" />
		<input type="submit" name="submit" value="Suchen" />
	</form>';
	
	
	$result = $file_db->query("SELECT * FROM tokens WHERE info LIKE '%{$s}%' OR tokenID LIKE '%{$s}%'");

	echo '<table><tr><th>UUID</th><th>Info</th><th>Guthaben</th><th>Kredit</th></tr>';
	foreach($result as $res) {
		echo '<tr><td>'. $res['tokenID'] .'</td><td>'. $res['info'] .'</td>
		<td>'. money_format('%=*^-14#8.2i', $res['cash']/100) .' Euro</td>
		<td>'. $res['saldo'] .'</td><td>
			[<a href="/?a=preedit&id='. $res['tokenID'] .'">Edit</a>]
		</td></tr>';
	}	
	echo '</table>';
}

?>
	</body>
</html>
