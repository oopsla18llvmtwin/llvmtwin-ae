extern crate foo;

pub fn main() {
    let mut gp1 = 0;
    let mut gp2 = 0;

    let (c, x) = foo::test(&mut gp1, &mut gp2, true, true);
    println!("c = {}, x = {}", c, x);
}
