import { ZComponent, ContextManager, Observable, Animation, Layer, LayerClip, Event } from "@zcomponent/core";

import { CameraEnvironmentMap as CameraEnvironmentMap_0 } from "@zcomponent/zappar-three/lib/components/environments/CameraEnvironmentMap";
import { DefaultCookieConsent as DefaultCookieConsent_1 } from "@zcomponent/core/lib/components/DefaultCookieConsent";
import { DefaultLoader as DefaultLoader_2 } from "@zcomponent/core/lib/components/DefaultLoader";
import { Group as Group_3 } from "@zcomponent/three/lib/components/Group";
import { DirectionalLight as DirectionalLight_4 } from "@zcomponent/three/lib/components/lights/DirectionalLight";
import { ImmersalAnchorGroup as ImmersalAnchorGroup_5 } from "@zcomponent/immersal/lib/components/ImmersalAnchorGroup";
import { ShadowPlane as ShadowPlane_6 } from "@zcomponent/three/lib/components/meshes/ShadowPlane";
import { WorldTracker as WorldTracker_7 } from "@zcomponent/zappar-three/lib/components/trackers/WorldTracker";
import { WorldTrackingUI as WorldTrackingUI_8 } from "@zcomponent/zappar-three/lib/components/WorldTrackingUI";
import { ZapparCamera as ZapparCamera_9 } from "@zcomponent/zappar-three/lib/components/cameras/Camera";
import { Box as Box_10 } from "@zcomponent/three/lib/components/meshes/Box";
import { HTML as HTML_11 } from "@zcomponent/three/lib/components/HTML";
import { CSS as CSS_12 } from "@zcomponent/html/lib/CSS";
import { Div as Div_13 } from "@zcomponent/html/lib/div";
import { ActivateState as ActivateState_14 } from "@zcomponent/core/lib/behaviors/ActivateState";
import { Img as Img_15 } from "@zcomponent/html/lib/img";
import { H2 as H2_16 } from "@zcomponent/html/lib/headings";
import { CameraTransform as CameraTransform_17 } from "@zcomponent/three/lib/components/transforms/CameraTransform";
import { LookAtNode as LookAtNode_18 } from "@zcomponent/three/lib/components/transforms/LookAtNode";
import { GLTF as GLTF_19 } from "@zcomponent/three/lib/components/models/GLTF";

interface ConstructorProps {

}

/**
* @zcomponent
* @zicon zcomponent
*/
declare class Comp extends ZComponent {

	constructor(contextManager: ContextManager, constructorProps: ConstructorProps);

	nodes: {
		CameraEnvironmentMap: CameraEnvironmentMap_0 & {
			behaviors: {

			}
		},
		DefaultCookieConsent: DefaultCookieConsent_1 & {
			behaviors: {

			}
		},
		DefaultLoader: DefaultLoader_2 & {
			behaviors: {

			}
		},
		Defaults: Group_3 & {
			behaviors: {

			}
		},
		DirectionalLight: DirectionalLight_4 & {
			behaviors: {

			}
		},
		ImmersalAnchorGroup: ImmersalAnchorGroup_5 & {
			behaviors: {

			}
		},
		ShadowPlane: ShadowPlane_6 & {
			behaviors: {

			}
		},
		WorldTracker: WorldTracker_7 & {
			behaviors: {

			}
		},
		WorldTrackingUI: WorldTrackingUI_8 & {
			behaviors: {

			}
		},
		ZapparCamera: ZapparCamera_9 & {
			behaviors: {

			}
		},
		Spot_1: Box_10 & {
			behaviors: {

			}
		},
		Spot_10: Box_10 & {
			behaviors: {

			}
		},
		HTML: HTML_11 & {
			behaviors: {

			}
		},
		styles_css: CSS_12 & {
			behaviors: {

			}
		},
		FooterContainer: Div_13 & {
			behaviors: {

			}
		},
		Spot1: Div_13 & {
			behaviors: {
				0: ActivateState_14,
				ActivateState: ActivateState_14,
			}
		},
		Img: Img_15 & {
			behaviors: {

			}
		},
		H2: H2_16 & {
			behaviors: {

			}
		},
		Spot10: Div_13 & {
			behaviors: {
				0: ActivateState_14,
				ActivateState: ActivateState_14,
			}
		},
		Img0: Img_15 & {
			behaviors: {

			}
		},
		H20: H2_16 & {
			behaviors: {

			}
		},
		CameraTransform: CameraTransform_17 & {
			behaviors: {

			}
		},
		LookAtNode: LookAtNode_18 & {
			behaviors: {

			}
		},
		arrow_01_glb: GLTF_19 & {
			behaviors: {

			}
		},
	};

	animation: Animation & { layers: {
		SwitchLocation: Layer & { clips: {
			Spot10: LayerClip;
			Spot20: LayerClip;
		}};
	}};

	/**
	 * The position, in 3D space, of this node relative to its parent. The three elements of the array correspond to the `x`, `y`, and `z` components of position.
	 * 
	 * @zprop
	 * @zdefault [0,0,0]
	 * @zgroup Transform
	 * @zgrouppriority 10
	 */
	public position: Observable<[x: number, y: number, z: number]>;

	/**
	 * The rotation, in three dimensions, of this node relative to its parent. The three elements of the array correspond to Euler angles - yaw, pitch and roll.
	 * 
	 * @zprop
	 * @zdefault [0,0,0]
	 * @zgroup Transform
	 * @zgrouppriority 10
	 */
	public rotation: Observable<[x: number, y: number, z: number]>;

	/**
	 * The scale, in three dimensions, of this node relative to its parent. The three elements of the array correspond to scales in the the `x`, `y`, and `z` axis.
	 * 
	 * @zprop
	 * @zdefault [1,1,1]
	 * @zgroup Transform
	 * @zgrouppriority 10
	 */
	public scale: Observable<[x: number, y: number, z: number]>;

	/**
	 * Determines if this object and its children are rendered to the screen.
	 * 
	 * @zprop
	 * @zdefault true
	 * @zgroup Appearance
	 * @zgrouppriority 11
	 */
	public visible: Observable<boolean>;
}

export default Comp;
