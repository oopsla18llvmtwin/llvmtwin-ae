#[inline(never)]
pub fn test(gp1: &mut usize, gp2: &mut usize, b1: bool, b2: bool) -> (i32, i32) {
    let mut g = 0;
    let mut c = 0;
    let y = 0;
    let mut x = 7777;
    let mut z = 8888;
    let mut p = &mut g as *const i32;

    {
        let mut q = &mut g;
        let mut r = &mut z;

        if b1 {
            p = (&y as *const i32).wrapping_offset(1);
        }

        if b2 {
            q = &mut x;
        }

        *gp1 = p as usize + 1234;
        if q as *const i32 == p {
            c = 1;
            *gp2 = (q as *const i32) as usize + 1234;
            r = q;
        }

        *r = 42;
    }

    return (c, x);
}
