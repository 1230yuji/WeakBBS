#!/usr/bin/perl

use DBI;

# init
$user = 'bbs';
$pass = 'gaiax';

my %param = map { /([^=]+)=(.+)/ } split /&/, $ENV{'QUERY_STRING'};

if ($param{'mode'} eq 'view') {
	&view( %param );
} elsif ( $param{'mode'} eq "edit") {
	&edit( %param );
} elsif ( $param{'mode'} eq "confirm") {
	&confirm( %param );
} elsif ( $param{'mode'} eq "finish") {
	&finish( %param );
} else {
	&view( %param );
}

exit;


# view (default)
sub view {
	my %param = @_;

	&setHeader;

	&connectDB;
	$sth = $db->prepare("SELECT * FROM bbs ORDER BY time DESC");
	$sth -> execute();
	&disconnectDB;

	print "<table>\n";
	print "<tr>\n";
	print "  <th>id</th>\n";
	print "  <th>time</th>\n";
	print "  <th>name</th>\n";
	print "  <th>message</th>\n";
	print "  <th></th>\n";
	print "</tr>\n";

	while(@data = $sth -> fetchrow_array){
		$id		= $data[0];
		$time		= $data[1];
		$name		= $data[2];
		$message	= $data[3];
		$display 	= $data[4];

		if ( $display == 1 ) {
			print "<tr>\n";
			print "  <td>$id</td>\n";
			print "  <td>$time</td>\n";
			print "  <td>$name</td>\n";
			print "  <td>$message</td>\n";
			print "  <td><a href=\"?mode=edit&id=$id\">編集</a></td>\n";
			print "</tr>\n";
		}
	}
	print "</table>\n";

	&setForm(%param);

	&setFooter;

}

sub edit {
	my %param = @_;
	
	&connectDB;
	$sth = $db->prepare("SELECT * FROM bbs WHERE id = $param{'id'}");
	$sth -> execute();
	&disconnectDB;
	
	&setHeader;


	while (@data = $sth -> fetchrow_array) {
		
		%data = (
			id => $data[0],
			time => $data[1],
			name => $data[2],
			message => $data[3],
			display => $data[4]
		);
		
	}
	
	&setForm(%data);
	
	&setFooter;

}

sub confirm {
	my %param = @_;

	&setHeader;
	
	$param{'name'} =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	$param{'message'} =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

	&setConfirm(%param);

	&setFooter;
}

sub finish {
	my %param = @_;
	
	&connectDB;
	#&insertValue(%param);
	$sql = &insertValue(%param);
	&disconnectDB;
	
	&setHeader;
	
	print <<"EOM";
done!</br></br>
<a href="$ENV{'SCRIPT_NAME'}">戻る</a>
$sql
EOM
	&setFooter;
}

# DB connect
sub connectDB {
	$db = DBI->connect('DBI:mysql:bbs:localhost', $user, $pass);
}

# DB disconnect
sub disconnectDB {
	$db->disconnect;
}

# Insert Values
sub insertValue {
	my %param = @_;

	#decode
	for my $key ( keys %param ) {
		$param{$key} =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$param{$key} =~ s/\+/ /g;
	}

	my $sql = qq/INSERT INTO bbs VALUES (NULL, NOW(), "$param{'name'}", "$param{'message'}", 1 );/;

	if ( $param{'id'} > 0 ) {
		$sql = qq/UPDATE bbs SET time = NOW(), name = "$param{'name'}", message="$param{'message'}" WHERE id = $param{'id'};/;
	}

	$sth = $db->prepare($sql);
	$sth -> execute();
	$sth -> finish();
	
}

# Parse values
sub readParse {
	my $query = $ENV{'QUERY_STRING'};
	

}

# Set Header
sub setHeader {
		print "Content-type: text/html\n\n";
		print <<"EOM";
<HTML>
<HEAD>
  <META http-equiv="Content-Type" content="text/html; charset=utf_8">
</HEAD>
<BODY>
<h1>セキュリティ的にとてもひどい掲示板</h1>
EOM

}


# Set Footer
sub setFooter {
	print "</body>\n";
	print "</html>\n";
}

sub setForm {
	my %param = @_;
	
	print <<"EOM";
<hr>
<form action="$ENV{'SCRIPT_NAME'}" method="GET">
  <input type="hidden" name="mode" value="confirm">
  <input type="hidden" name="id" value="$param{'id'}">
  名前</br>
  <input type="text" name="name" size="40" value="$param{'name'}"></br>
  内容</br>
  <textarea name="message" rows="4" cols="40">$param{'message'}</textarea></br>
  <input type="submit" value="送信">
</form>
EOM
}

sub setConfirm {
	my %param = @_;
	
	print <<"EOM";
<form action="$ENV{'SCRIPT_NAME'}" method="GET">
  これでいい？</br>
  名前：$param{'name'}</br>
  内容：$param{'message'}</br>
  <input type="hidden" name="mode" value="finish">
  <input type="hidden" name="name" value="$param{'name'}">
  <input type="hidden" name="message" value="$param{'message'}">
  <input type="hidden" name=id value="$param{'id'}">
  <input type="submit" value="おｋ">
</form>
EOM
}


