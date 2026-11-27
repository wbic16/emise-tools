//! Minimal phext reader, written from scratch on std only.
//!
//! Phext addresses text in 9 dimensions; scrolls are separated by the
//! level delimiter bytes (library..scroll):
//!   0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17
//! Reading walks the bytes with a coordinate state machine: a delimiter
//! at level L advances coordinate L by one and resets all finer levels
//! to 1. The text between delimiters is the scroll at the coordinate
//! the machine is sitting on when the next delimiter (or EOF) arrives.

pub const LEVEL_BYTES: [u8; 9] = [0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17];

#[derive(Debug, Clone)]
pub struct Scroll {
    pub coord: [u32; 9],
    pub text: String,
}

impl Scroll {
    pub fn coord_string(&self) -> String {
        let c = self.coord;
        format!(
            "{}.{}.{}/{}.{}.{}/{}.{}.{}",
            c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8]
        )
    }
}

fn is_delim(b: u8) -> Option<usize> {
    LEVEL_BYTES.iter().position(|&d| d == b)
}

/// Parse a whole phext document into its scrolls, in document order.
pub fn parse(bytes: &[u8]) -> Vec<Scroll> {
    let mut scrolls = Vec::new();
    let mut coord = [1u32; 9];
    let mut cur: Vec<u8> = Vec::new();
    let mut started = false;
    for &b in bytes {
        if let Some(level) = is_delim(b) {
            if started || !cur.is_empty() {
                scrolls.push(Scroll {
                    coord,
                    text: String::from_utf8_lossy(&cur).into_owned(),
                });
            }
            cur.clear();
            started = true;
            coord[level] += 1;
            for finer in coord.iter_mut().skip(level + 1) {
                *finer = 1;
            }
        } else {
            cur.push(b);
        }
    }
    if started || !cur.is_empty() {
        scrolls.push(Scroll {
            coord,
            text: String::from_utf8_lossy(&cur).into_owned(),
        });
    }
    scrolls
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn two_scrolls_one_volume_apart() {
        // home scroll, then scroll delimiter advances the last level.
        let mut doc = b"home".to_vec();
        doc.push(LEVEL_BYTES[8]);
        doc.extend_from_slice(b"second");
        let s = parse(&doc);
        assert_eq!(s.len(), 2);
        assert_eq!(s[0].text, "home");
        assert_eq!(s[0].coord, [1; 9]);
        assert_eq!(s[1].text, "second");
        assert_eq!(s[1].coord[8], 2);
    }

    #[test]
    fn volume_delimiter_resets_finer_levels() {
        let mut doc = b"a".to_vec();
        doc.push(LEVEL_BYTES[8]); // scroll -> 2
        doc.extend_from_slice(b"b");
        doc.push(LEVEL_BYTES[4]); // volume -> 2, finer reset
        doc.extend_from_slice(b"c");
        let s = parse(&doc);
        assert_eq!(s.len(), 3);
        assert_eq!(s[2].coord[4], 2);
        assert_eq!(s[2].coord[8], 1);
        assert_eq!(s[2].text, "c");
    }
}
