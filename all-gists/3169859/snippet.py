#!/usr/bin/env perl

use warnings;use strict;
use Bio::SeqIO;

my $in = Bio::SeqIO->new(-file => shift, '-format' => 'Fasta');

while(my $rec = $in->next_seq() ){
  print join(" ",$rec->display_id,$rec->length)."\n";
}
