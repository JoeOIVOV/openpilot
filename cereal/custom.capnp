using Cxx = import "./include/c++.capnp";
$Cxx.namespace("cereal");

@0xb526ba661d550a59;

# custom.capnp: a home for empty structs reserved for custom forks
# These structs are guaranteed to remain reserved and empty in mainline
# cereal, so use these if you want custom events in your fork.

# you can rename the struct, but don't change the identifier
struct ControlsStateExt @0x81c2f05a394cf4af {
  alkaActive @0 :Bool;
  alkaEnabled @1 :Bool;
}

struct LongitudinalPlanExt @0xaedffd8f31e7b55d {
  de2eIsBlended @0 :Bool;
  de2eIsEnabled @1 :Bool;
  altDrivingPersonalityIsActive @2 :Bool;
}

enum LaneChangeAssistMode {
  stock @0;
  disable @1;
  hold @2;
  auto @3;
}

struct TeToo @0xf35cc4560bbf6ec2 {
  lat @0 :Float32;
  lon @1 :Float32;
  bearing @2 :Float32;
  name @3 :Text;
  maxspeed @4 :Float32;
  tags @5 :Text;

  updatingData @6 :Bool;
  nearestFeatures @7 :List(Feature);

  struct Feature {
    id @0 :Text;
    type @1 :FeatureType;
    lat @2 :Float32;
    lon @3 :Float32;
    bearing @4 :Float32;
    distance @5 :Float32;
    tags @6 :Text;
    probability @7 :Float32;
  }

  enum FeatureType {
    trafficSignal @0;
    speedCamera @1;
  }

}

struct CustomReserved3 @0xda96579883444c35 {
}

struct CustomReserved4 @0x80ae746ee2596b11 {
}

struct CustomReserved5 @0xa5cd762cd951a455 {
}

struct CustomReserved6 @0xf98d843bfd7004a3 {
}

struct CustomReserved7 @0xb86e6369214c01c8 {
}

struct CustomReserved8 @0xf416ec09499d9d19 {
}

struct CustomReserved9 @0xa1680744031fdb2d {
}
