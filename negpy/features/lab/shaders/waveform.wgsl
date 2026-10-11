@group(0) @binding(0) var input_tex: texture_2d<f32>;
// 128 luma bins x 256 image columns, indexed bin * 256 + col, bin 0 = black. Mirrors
// WAVEFORM_BINS / WAVEFORM_COLS and waveform() in features/exposure/analysis.py.
@group(0) @binding(1) var<storage, read_write> bins: array<atomic<u32>, 32768>;

const COLS = 256u;
const BINS = 128.0;
const LUMA_COEFFS = vec3<f32>(0.2126, 0.7152, 0.0722);

// Working-space OETF (Adobe RGB: pure 563/256 gamma). Mirrors output_encode.wgsl.
fn oetf_encode(c: vec3<f32>) -> vec3<f32> {
    let x = clamp(c, vec3<f32>(0.0), vec3<f32>(1.0));
    return pow(x, vec3<f32>(0.45470693));
}

@compute @workgroup_size(16, 16)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
    let dims = textureDimensions(input_tex);
    if (gid.x >= dims.x || gid.y >= dims.y) {
        return;
    }

    // Same encode and luma as metrics.wgsl, so the waveform and the L histogram describe one image.
    let color = oetf_encode(textureLoad(input_tex, vec2<i32>(i32(gid.x), i32(gid.y)), 0).rgb);
    let luma = dot(color, LUMA_COEFFS);
    let col = min(gid.x * COLS / dims.x, COLS - 1u);
    let bin = u32(clamp(floor(luma * BINS), 0.0, BINS - 1.0));

    atomicAdd(&bins[bin * COLS + col], 1u);
}
