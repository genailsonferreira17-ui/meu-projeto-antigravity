import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const NAVY = "#12244a";
const GOLD = "#c9a45c";
const WHITE = "#ffffff";
const FONT = "Helvetica, Arial, sans-serif";

const fadeInOut = (frame: number, total: number) =>
  interpolate(frame, [0, 15, total - 15, total], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const Logo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 200 } });
  return (
    <AbsoluteFill
      style={{
        backgroundColor: NAVY,
        justifyContent: "center",
        alignItems: "center",
        opacity: fadeInOut(frame, 90),
      }}
    >
      <Img
        src={staticFile("logo.jpg")}
        style={{ height: 900, transform: `scale(${0.85 + 0.15 * scale})` }}
      />
    </AbsoluteFill>
  );
};

const Counter: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame: frame - 10, fps, config: { damping: 200 }, durationInFrames: 60 });
  const value = Math.round(21000 * progress);
  const label = spring({ frame: frame - 40, fps, config: { damping: 200 } });
  const barWidth = interpolate(progress, [0, 1], [0, 1]);
  const formatted = value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  return (
    <AbsoluteFill
      style={{
        backgroundColor: NAVY,
        justifyContent: "center",
        alignItems: "center",
        fontFamily: FONT,
        opacity: fadeInOut(frame, 120),
      }}
    >
      <div style={{ color: GOLD, fontSize: 40, letterSpacing: 8, fontWeight: 700 }}>
        FRANCE INVISIBLE
      </div>
      <div style={{ color: WHITE, fontSize: 320, fontWeight: 900, lineHeight: 1.1 }}>
        {formatted}
      </div>
      <div
        style={{
          color: WHITE,
          fontSize: 64,
          fontWeight: 700,
          opacity: label,
          transform: `translateY(${(1 - label) * 30}px)`,
        }}
      >
        pharmacies en France
      </div>
      <div
        style={{
          marginTop: 60,
          width: 1000,
          height: 24,
          borderRadius: 12,
          backgroundColor: "rgba(255,255,255,0.15)",
        }}
      >
        <div
          style={{
            width: `${barWidth * 100}%`,
            height: "100%",
            borderRadius: 12,
            backgroundColor: GOLD,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

const Chapter: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 200 } });
  const lineWidth = interpolate(enter, [0, 1], [0, 220]);
  return (
    <AbsoluteFill
      style={{
        backgroundColor: NAVY,
        justifyContent: "center",
        paddingLeft: 200,
        fontFamily: FONT,
        opacity: fadeInOut(frame, 90),
      }}
    >
      <div style={{ color: GOLD, fontSize: 56, fontWeight: 700, letterSpacing: 6 }}>
        CHAPITRE 1
      </div>
      <div
        style={{ width: lineWidth, height: 8, backgroundColor: GOLD, margin: "28px 0" }}
      />
      <div
        style={{
          color: WHITE,
          fontSize: 104,
          fontWeight: 900,
          maxWidth: 1400,
          lineHeight: 1.1,
          opacity: enter,
          transform: `translateX(${(1 - enter) * -60}px)`,
        }}
      >
        Une pharmacie à chaque coin de rue
      </div>
    </AbsoluteFill>
  );
};

export const Teste: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: NAVY }}>
    <Sequence from={0} durationInFrames={90}>
      <Logo />
    </Sequence>
    <Sequence from={90} durationInFrames={120}>
      <Counter />
    </Sequence>
    <Sequence from={210} durationInFrames={90}>
      <Chapter />
    </Sequence>
  </AbsoluteFill>
);
