use std::io;fn main( ){let mut input=String::new();
println!("Enter number:");
io::stdin().read_line(&mut input).unwrap();
let n:i32=input.trim().parse().unwrap();
if n<=1{println!("Not prime");return;}
let mut i=2;let mut flag=false;
while i<n{if n%i==0{flag=true;break;}i+=1;}
if flag==false{println!("Prime");}else{println!("Not prime");}}
