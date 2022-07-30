#!/usr/bin/perl

# uses rsync to fetch configs and stores them in $target dir
# exports crontab of user pi and root

use strict;
use warnings;
use 5.010;    # say

my $target = '/home/pi/sicher-configs';

my @list = qw (
    /etc/grafana
    /etc/collectd
    /etc/influxdb
    /home/pi/.bashrc
);

foreach my $item ( @list ) {
  $_ = "sudo rsync -ru --delete --delete-excluded $item $target";
  my $returncode = system $_;
  if ( $returncode != 0 ) {
    say "ERROR in backup of $item";
  }
} ## end foreach my $item ( @list )


print `crontab -l      > $target/crontab-pi.txt`;
print `sudo crontab -l > $target/crontab-root.txt`;
