import { WireType } from "@protobuf-ts/runtime";
import { UnknownFieldHandler } from "@protobuf-ts/runtime";
import { reflectionMergePartial } from "@protobuf-ts/runtime";
import { MessageType } from "@protobuf-ts/runtime";
/**
 * Enum for common spacing tokens
 *
 * @generated from protobuf enum sads.v1.SadsSpacingToken
 */
export var SadsSpacingToken;
(function (SadsSpacingToken) {
    /**
     * Default, should not be used directly for styling
     *
     * @generated from protobuf enum value: SPACING_TOKEN_UNSPECIFIED = 0;
     */
    SadsSpacingToken[SadsSpacingToken["SPACING_TOKEN_UNSPECIFIED"] = 0] = "SPACING_TOKEN_UNSPECIFIED";
    /**
     * "0"
     *
     * @generated from protobuf enum value: SPACING_TOKEN_NONE = 1;
     */
    SadsSpacingToken[SadsSpacingToken["SPACING_TOKEN_NONE"] = 1] = "SPACING_TOKEN_NONE";
    /**
     * e.g., "0.25rem"
     *
     * @generated from protobuf enum value: SPACING_TOKEN_XS = 2;
     */
    SadsSpacingToken[SadsSpacingToken["SPACING_TOKEN_XS"] = 2] = "SPACING_TOKEN_XS";
    /**
     * e.g., "0.5rem"
     *
     * @generated from protobuf enum value: SPACING_TOKEN_S = 3;
     */
    SadsSpacingToken[SadsSpacingToken["SPACING_TOKEN_S"] = 3] = "SPACING_TOKEN_S";
    /**
     * e.g., "1rem"
     *
     * @generated from protobuf enum value: SPACING_TOKEN_M = 4;
     */
    SadsSpacingToken[SadsSpacingToken["SPACING_TOKEN_M"] = 4] = "SPACING_TOKEN_M";
    /**
     * e.g., "1.5rem"
     *
     * @generated from protobuf enum value: SPACING_TOKEN_L = 5;
     */
    SadsSpacingToken[SadsSpacingToken["SPACING_TOKEN_L"] = 5] = "SPACING_TOKEN_L";
    /**
     * e.g., "2rem"
     *
     * @generated from protobuf enum value: SPACING_TOKEN_XL = 6;
     */
    SadsSpacingToken[SadsSpacingToken["SPACING_TOKEN_XL"] = 6] = "SPACING_TOKEN_XL";
    /**
     * e.g., "4rem"
     *
     * @generated from protobuf enum value: SPACING_TOKEN_XXL = 7;
     */
    SadsSpacingToken[SadsSpacingToken["SPACING_TOKEN_XXL"] = 7] = "SPACING_TOKEN_XXL";
    /**
     * "auto"
     *
     * @generated from protobuf enum value: SPACING_TOKEN_AUTO = 8;
     */
    SadsSpacingToken[SadsSpacingToken["SPACING_TOKEN_AUTO"] = 8] = "SPACING_TOKEN_AUTO";
})(SadsSpacingToken || (SadsSpacingToken = {}));
/**
 * Enum for common color semantic tokens
 * These would map to keys in the theme's color palette.
 *
 * @generated from protobuf enum sads.v1.SadsColorToken
 */
export var SadsColorToken;
(function (SadsColorToken) {
    /**
     * @generated from protobuf enum value: COLOR_TOKEN_UNSPECIFIED = 0;
     */
    SadsColorToken[SadsColorToken["COLOR_TOKEN_UNSPECIFIED"] = 0] = "COLOR_TOKEN_UNSPECIFIED";
    /**
     * "transparent"
     *
     * @generated from protobuf enum value: COLOR_TOKEN_TRANSPARENT = 1;
     */
    SadsColorToken[SadsColorToken["COLOR_TOKEN_TRANSPARENT"] = 1] = "COLOR_TOKEN_TRANSPARENT";
    /**
     * @generated from protobuf enum value: COLOR_TOKEN_SURFACE = 2;
     */
    SadsColorToken[SadsColorToken["COLOR_TOKEN_SURFACE"] = 2] = "COLOR_TOKEN_SURFACE";
    /**
     * For dark mode variant of SURFACE
     *
     * @generated from protobuf enum value: COLOR_TOKEN_SURFACE_DARK = 3;
     */
    SadsColorToken[SadsColorToken["COLOR_TOKEN_SURFACE_DARK"] = 3] = "COLOR_TOKEN_SURFACE_DARK";
    /**
     * @generated from protobuf enum value: COLOR_TOKEN_SURFACE_ACCENT = 4;
     */
    SadsColorToken[SadsColorToken["COLOR_TOKEN_SURFACE_ACCENT"] = 4] = "COLOR_TOKEN_SURFACE_ACCENT";
    /**
     * For dark mode variant of SURFACE_ACCENT
     *
     * @generated from protobuf enum value: COLOR_TOKEN_SURFACE_ACCENT_DARK = 5;
     */
    SadsColorToken[SadsColorToken["COLOR_TOKEN_SURFACE_ACCENT_DARK"] = 5] = "COLOR_TOKEN_SURFACE_ACCENT_DARK";
    /**
     * @generated from protobuf enum value: COLOR_TOKEN_TEXT_PRIMARY = 6;
     */
    SadsColorToken[SadsColorToken["COLOR_TOKEN_TEXT_PRIMARY"] = 6] = "COLOR_TOKEN_TEXT_PRIMARY";
    /**
     * For dark mode variant of TEXT_PRIMARY
     *
     * @generated from protobuf enum value: COLOR_TOKEN_TEXT_PRIMARY_DARK = 7;
     */
    SadsColorToken[SadsColorToken["COLOR_TOKEN_TEXT_PRIMARY_DARK"] = 7] = "COLOR_TOKEN_TEXT_PRIMARY_DARK";
    /**
     * @generated from protobuf enum value: COLOR_TOKEN_TEXT_ACCENT = 8;
     */
    SadsColorToken[SadsColorToken["COLOR_TOKEN_TEXT_ACCENT"] = 8] = "COLOR_TOKEN_TEXT_ACCENT";
    /**
     * For dark mode variant of TEXT_ACCENT
     *
     * @generated from protobuf enum value: COLOR_TOKEN_TEXT_ACCENT_DARK = 9;
     */
    SadsColorToken[SadsColorToken["COLOR_TOKEN_TEXT_ACCENT_DARK"] = 9] = "COLOR_TOKEN_TEXT_ACCENT_DARK";
    /**
     * Example, could be derived or a direct theme key
     *
     * @generated from protobuf enum value: COLOR_TOKEN_BORDER_ACCENT = 10;
     */
    SadsColorToken[SadsColorToken["COLOR_TOKEN_BORDER_ACCENT"] = 10] = "COLOR_TOKEN_BORDER_ACCENT";
})(SadsColorToken || (SadsColorToken = {}));
/**
 * Enum for font weight tokens
 *
 * @generated from protobuf enum sads.v1.SadsFontWeightToken
 */
export var SadsFontWeightToken;
(function (SadsFontWeightToken) {
    /**
     * @generated from protobuf enum value: FONT_WEIGHT_TOKEN_UNSPECIFIED = 0;
     */
    SadsFontWeightToken[SadsFontWeightToken["FONT_WEIGHT_TOKEN_UNSPECIFIED"] = 0] = "FONT_WEIGHT_TOKEN_UNSPECIFIED";
    /**
     * e.g., "400"
     *
     * @generated from protobuf enum value: FONT_WEIGHT_TOKEN_NORMAL = 1;
     */
    SadsFontWeightToken[SadsFontWeightToken["FONT_WEIGHT_TOKEN_NORMAL"] = 1] = "FONT_WEIGHT_TOKEN_NORMAL";
    /**
     * e.g., "700"
     *
     * @generated from protobuf enum value: FONT_WEIGHT_TOKEN_BOLD = 2;
     */
    SadsFontWeightToken[SadsFontWeightToken["FONT_WEIGHT_TOKEN_BOLD"] = 2] = "FONT_WEIGHT_TOKEN_BOLD";
})(SadsFontWeightToken || (SadsFontWeightToken = {}));
/**
 * Enum for border radius tokens
 *
 * @generated from protobuf enum sads.v1.SadsBorderRadiusToken
 */
export var SadsBorderRadiusToken;
(function (SadsBorderRadiusToken) {
    /**
     * @generated from protobuf enum value: BORDER_RADIUS_TOKEN_UNSPECIFIED = 0;
     */
    SadsBorderRadiusToken[SadsBorderRadiusToken["BORDER_RADIUS_TOKEN_UNSPECIFIED"] = 0] = "BORDER_RADIUS_TOKEN_UNSPECIFIED";
    /**
     * "0"
     *
     * @generated from protobuf enum value: BORDER_RADIUS_TOKEN_NONE = 1;
     */
    SadsBorderRadiusToken[SadsBorderRadiusToken["BORDER_RADIUS_TOKEN_NONE"] = 1] = "BORDER_RADIUS_TOKEN_NONE";
    /**
     * e.g., "4px"
     *
     * @generated from protobuf enum value: BORDER_RADIUS_TOKEN_S = 2;
     */
    SadsBorderRadiusToken[SadsBorderRadiusToken["BORDER_RADIUS_TOKEN_S"] = 2] = "BORDER_RADIUS_TOKEN_S";
    /**
     * e.g., "8px"
     *
     * @generated from protobuf enum value: BORDER_RADIUS_TOKEN_M = 3;
     */
    SadsBorderRadiusToken[SadsBorderRadiusToken["BORDER_RADIUS_TOKEN_M"] = 3] = "BORDER_RADIUS_TOKEN_M";
    /**
     * e.g., "16px"
     *
     * @generated from protobuf enum value: BORDER_RADIUS_TOKEN_L = 4;
     */
    SadsBorderRadiusToken[SadsBorderRadiusToken["BORDER_RADIUS_TOKEN_L"] = 4] = "BORDER_RADIUS_TOKEN_L";
})(SadsBorderRadiusToken || (SadsBorderRadiusToken = {}));
// @generated message type with reflection information, may provide speed optimized methods
class SadsAttributeValue$Type extends MessageType {
    constructor() {
        super("sads.v1.SadsAttributeValue", [
            { no: 1, name: "spacing_token", kind: "enum", oneof: "valueType", T: () => ["sads.v1.SadsSpacingToken", SadsSpacingToken] },
            { no: 2, name: "color_token", kind: "enum", oneof: "valueType", T: () => ["sads.v1.SadsColorToken", SadsColorToken] },
            { no: 3, name: "font_weight_token", kind: "enum", oneof: "valueType", T: () => ["sads.v1.SadsFontWeightToken", SadsFontWeightToken] },
            { no: 4, name: "border_radius_token", kind: "enum", oneof: "valueType", T: () => ["sads.v1.SadsBorderRadiusToken", SadsBorderRadiusToken] },
            { no: 5, name: "font_size_value", kind: "scalar", oneof: "valueType", T: 9 /*ScalarType.STRING*/ },
            { no: 6, name: "custom_value", kind: "scalar", oneof: "valueType", T: 9 /*ScalarType.STRING*/ }
        ]);
    }
    create(value) {
        const message = globalThis.Object.create((this.messagePrototype));
        message.valueType = { oneofKind: undefined };
        if (value !== undefined)
            reflectionMergePartial(this, message, value);
        return message;
    }
    internalBinaryRead(reader, length, options, target) {
        let message = target ?? this.create(), end = reader.pos + length;
        while (reader.pos < end) {
            let [fieldNo, wireType] = reader.tag();
            switch (fieldNo) {
                case /* sads.v1.SadsSpacingToken spacing_token */ 1:
                    message.valueType = {
                        oneofKind: "spacingToken",
                        spacingToken: reader.int32()
                    };
                    break;
                case /* sads.v1.SadsColorToken color_token */ 2:
                    message.valueType = {
                        oneofKind: "colorToken",
                        colorToken: reader.int32()
                    };
                    break;
                case /* sads.v1.SadsFontWeightToken font_weight_token */ 3:
                    message.valueType = {
                        oneofKind: "fontWeightToken",
                        fontWeightToken: reader.int32()
                    };
                    break;
                case /* sads.v1.SadsBorderRadiusToken border_radius_token */ 4:
                    message.valueType = {
                        oneofKind: "borderRadiusToken",
                        borderRadiusToken: reader.int32()
                    };
                    break;
                case /* string font_size_value */ 5:
                    message.valueType = {
                        oneofKind: "fontSizeValue",
                        fontSizeValue: reader.string()
                    };
                    break;
                case /* string custom_value */ 6:
                    message.valueType = {
                        oneofKind: "customValue",
                        customValue: reader.string()
                    };
                    break;
                default:
                    let u = options.readUnknownField;
                    if (u === "throw")
                        throw new globalThis.Error(`Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`);
                    let d = reader.skip(wireType);
                    if (u !== false)
                        (u === true ? UnknownFieldHandler.onRead : u)(this.typeName, message, fieldNo, wireType, d);
            }
        }
        return message;
    }
    internalBinaryWrite(message, writer, options) {
        /* sads.v1.SadsSpacingToken spacing_token = 1; */
        if (message.valueType.oneofKind === "spacingToken")
            writer.tag(1, WireType.Varint).int32(message.valueType.spacingToken);
        /* sads.v1.SadsColorToken color_token = 2; */
        if (message.valueType.oneofKind === "colorToken")
            writer.tag(2, WireType.Varint).int32(message.valueType.colorToken);
        /* sads.v1.SadsFontWeightToken font_weight_token = 3; */
        if (message.valueType.oneofKind === "fontWeightToken")
            writer.tag(3, WireType.Varint).int32(message.valueType.fontWeightToken);
        /* sads.v1.SadsBorderRadiusToken border_radius_token = 4; */
        if (message.valueType.oneofKind === "borderRadiusToken")
            writer.tag(4, WireType.Varint).int32(message.valueType.borderRadiusToken);
        /* string font_size_value = 5; */
        if (message.valueType.oneofKind === "fontSizeValue")
            writer.tag(5, WireType.LengthDelimited).string(message.valueType.fontSizeValue);
        /* string custom_value = 6; */
        if (message.valueType.oneofKind === "customValue")
            writer.tag(6, WireType.LengthDelimited).string(message.valueType.customValue);
        let u = options.writeUnknownFields;
        if (u !== false)
            (u == true ? UnknownFieldHandler.onWrite : u)(this.typeName, message, writer);
        return writer;
    }
}
/**
 * @generated MessageType for protobuf message sads.v1.SadsAttributeValue
 */
export const SadsAttributeValue = new SadsAttributeValue$Type();
// @generated message type with reflection information, may provide speed optimized methods
class SadsStylingSet$Type extends MessageType {
    constructor() {
        super("sads.v1.SadsStylingSet", [
            { no: 1, name: "attributes", kind: "map", K: 9 /*ScalarType.STRING*/, V: { kind: "message", T: () => SadsAttributeValue } }
        ]);
    }
    create(value) {
        const message = globalThis.Object.create((this.messagePrototype));
        message.attributes = {};
        if (value !== undefined)
            reflectionMergePartial(this, message, value);
        return message;
    }
    internalBinaryRead(reader, length, options, target) {
        let message = target ?? this.create(), end = reader.pos + length;
        while (reader.pos < end) {
            let [fieldNo, wireType] = reader.tag();
            switch (fieldNo) {
                case /* map<string, sads.v1.SadsAttributeValue> attributes */ 1:
                    this.binaryReadMap1(message.attributes, reader, options);
                    break;
                default:
                    let u = options.readUnknownField;
                    if (u === "throw")
                        throw new globalThis.Error(`Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`);
                    let d = reader.skip(wireType);
                    if (u !== false)
                        (u === true ? UnknownFieldHandler.onRead : u)(this.typeName, message, fieldNo, wireType, d);
            }
        }
        return message;
    }
    binaryReadMap1(map, reader, options) {
        let len = reader.uint32(), end = reader.pos + len, key, val;
        while (reader.pos < end) {
            let [fieldNo, wireType] = reader.tag();
            switch (fieldNo) {
                case 1:
                    key = reader.string();
                    break;
                case 2:
                    val = SadsAttributeValue.internalBinaryRead(reader, reader.uint32(), options);
                    break;
                default: throw new globalThis.Error("unknown map entry field for sads.v1.SadsStylingSet.attributes");
            }
        }
        map[key ?? ""] = val ?? SadsAttributeValue.create();
    }
    internalBinaryWrite(message, writer, options) {
        /* map<string, sads.v1.SadsAttributeValue> attributes = 1; */
        for (let k of globalThis.Object.keys(message.attributes)) {
            writer.tag(1, WireType.LengthDelimited).fork().tag(1, WireType.LengthDelimited).string(k);
            writer.tag(2, WireType.LengthDelimited).fork();
            SadsAttributeValue.internalBinaryWrite(message.attributes[k], writer, options);
            writer.join().join();
        }
        let u = options.writeUnknownFields;
        if (u !== false)
            (u == true ? UnknownFieldHandler.onWrite : u)(this.typeName, message, writer);
        return writer;
    }
}
/**
 * @generated MessageType for protobuf message sads.v1.SadsStylingSet
 */
export const SadsStylingSet = new SadsStylingSet$Type();
// @generated message type with reflection information, may provide speed optimized methods
class SadsResponsiveStyle$Type extends MessageType {
    constructor() {
        super("sads.v1.SadsResponsiveStyle", [
            { no: 1, name: "breakpoint_key", kind: "scalar", T: 9 /*ScalarType.STRING*/ },
            { no: 2, name: "styles", kind: "message", T: () => SadsStylingSet }
        ]);
    }
    create(value) {
        const message = globalThis.Object.create((this.messagePrototype));
        message.breakpointKey = "";
        if (value !== undefined)
            reflectionMergePartial(this, message, value);
        return message;
    }
    internalBinaryRead(reader, length, options, target) {
        let message = target ?? this.create(), end = reader.pos + length;
        while (reader.pos < end) {
            let [fieldNo, wireType] = reader.tag();
            switch (fieldNo) {
                case /* string breakpoint_key */ 1:
                    message.breakpointKey = reader.string();
                    break;
                case /* sads.v1.SadsStylingSet styles */ 2:
                    message.styles = SadsStylingSet.internalBinaryRead(reader, reader.uint32(), options, message.styles);
                    break;
                default:
                    let u = options.readUnknownField;
                    if (u === "throw")
                        throw new globalThis.Error(`Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`);
                    let d = reader.skip(wireType);
                    if (u !== false)
                        (u === true ? UnknownFieldHandler.onRead : u)(this.typeName, message, fieldNo, wireType, d);
            }
        }
        return message;
    }
    internalBinaryWrite(message, writer, options) {
        /* string breakpoint_key = 1; */
        if (message.breakpointKey !== "")
            writer.tag(1, WireType.LengthDelimited).string(message.breakpointKey);
        /* sads.v1.SadsStylingSet styles = 2; */
        if (message.styles)
            SadsStylingSet.internalBinaryWrite(message.styles, writer.tag(2, WireType.LengthDelimited).fork(), options).join();
        let u = options.writeUnknownFields;
        if (u !== false)
            (u == true ? UnknownFieldHandler.onWrite : u)(this.typeName, message, writer);
        return writer;
    }
}
/**
 * @generated MessageType for protobuf message sads.v1.SadsResponsiveStyle
 */
export const SadsResponsiveStyle = new SadsResponsiveStyle$Type();
// @generated message type with reflection information, may provide speed optimized methods
class SadsElementStyles$Type extends MessageType {
    constructor() {
        super("sads.v1.SadsElementStyles", [
            { no: 1, name: "base_styles", kind: "message", T: () => SadsStylingSet },
            { no: 2, name: "responsive_styles", kind: "message", repeat: 2 /*RepeatType.UNPACKED*/, T: () => SadsResponsiveStyle }
        ]);
    }
    create(value) {
        const message = globalThis.Object.create((this.messagePrototype));
        message.responsiveStyles = [];
        if (value !== undefined)
            reflectionMergePartial(this, message, value);
        return message;
    }
    internalBinaryRead(reader, length, options, target) {
        let message = target ?? this.create(), end = reader.pos + length;
        while (reader.pos < end) {
            let [fieldNo, wireType] = reader.tag();
            switch (fieldNo) {
                case /* optional sads.v1.SadsStylingSet base_styles */ 1:
                    message.baseStyles = SadsStylingSet.internalBinaryRead(reader, reader.uint32(), options, message.baseStyles);
                    break;
                case /* repeated sads.v1.SadsResponsiveStyle responsive_styles */ 2:
                    message.responsiveStyles.push(SadsResponsiveStyle.internalBinaryRead(reader, reader.uint32(), options));
                    break;
                default:
                    let u = options.readUnknownField;
                    if (u === "throw")
                        throw new globalThis.Error(`Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`);
                    let d = reader.skip(wireType);
                    if (u !== false)
                        (u === true ? UnknownFieldHandler.onRead : u)(this.typeName, message, fieldNo, wireType, d);
            }
        }
        return message;
    }
    internalBinaryWrite(message, writer, options) {
        /* optional sads.v1.SadsStylingSet base_styles = 1; */
        if (message.baseStyles)
            SadsStylingSet.internalBinaryWrite(message.baseStyles, writer.tag(1, WireType.LengthDelimited).fork(), options).join();
        /* repeated sads.v1.SadsResponsiveStyle responsive_styles = 2; */
        for (let i = 0; i < message.responsiveStyles.length; i++)
            SadsResponsiveStyle.internalBinaryWrite(message.responsiveStyles[i], writer.tag(2, WireType.LengthDelimited).fork(), options).join();
        let u = options.writeUnknownFields;
        if (u !== false)
            (u == true ? UnknownFieldHandler.onWrite : u)(this.typeName, message, writer);
        return writer;
    }
}
/**
 * @generated MessageType for protobuf message sads.v1.SadsElementStyles
 */
export const SadsElementStyles = new SadsElementStyles$Type();
// @generated message type with reflection information, may provide speed optimized methods
class SadsProcessingContext$Type extends MessageType {
    constructor() {
        super("sads.v1.SadsProcessingContext", [
            { no: 1, name: "is_dark_mode", kind: "scalar", T: 8 /*ScalarType.BOOL*/ }
        ]);
    }
    create(value) {
        const message = globalThis.Object.create((this.messagePrototype));
        message.isDarkMode = false;
        if (value !== undefined)
            reflectionMergePartial(this, message, value);
        return message;
    }
    internalBinaryRead(reader, length, options, target) {
        let message = target ?? this.create(), end = reader.pos + length;
        while (reader.pos < end) {
            let [fieldNo, wireType] = reader.tag();
            switch (fieldNo) {
                case /* bool is_dark_mode */ 1:
                    message.isDarkMode = reader.bool();
                    break;
                default:
                    let u = options.readUnknownField;
                    if (u === "throw")
                        throw new globalThis.Error(`Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`);
                    let d = reader.skip(wireType);
                    if (u !== false)
                        (u === true ? UnknownFieldHandler.onRead : u)(this.typeName, message, fieldNo, wireType, d);
            }
        }
        return message;
    }
    internalBinaryWrite(message, writer, options) {
        /* bool is_dark_mode = 1; */
        if (message.isDarkMode !== false)
            writer.tag(1, WireType.Varint).bool(message.isDarkMode);
        let u = options.writeUnknownFields;
        if (u !== false)
            (u == true ? UnknownFieldHandler.onWrite : u)(this.typeName, message, writer);
        return writer;
    }
}
/**
 * @generated MessageType for protobuf message sads.v1.SadsProcessingContext
 */
export const SadsProcessingContext = new SadsProcessingContext$Type();
// @generated message type with reflection information, may provide speed optimized methods
class ResolveSadsStylesRequest$Type extends MessageType {
    constructor() {
        super("sads.v1.ResolveSadsStylesRequest", [
            { no: 1, name: "element_styles", kind: "message", T: () => SadsElementStyles },
            { no: 2, name: "context", kind: "message", T: () => SadsProcessingContext },
            { no: 3, name: "theme_colors_json", kind: "scalar", T: 9 /*ScalarType.STRING*/ },
            { no: 4, name: "theme_spacing_json", kind: "scalar", T: 9 /*ScalarType.STRING*/ },
            { no: 5, name: "theme_font_size_json", kind: "scalar", T: 9 /*ScalarType.STRING*/ },
            { no: 6, name: "theme_breakpoints_json", kind: "scalar", T: 9 /*ScalarType.STRING*/ }
        ]);
    }
    create(value) {
        const message = globalThis.Object.create((this.messagePrototype));
        message.themeColorsJson = "";
        message.themeSpacingJson = "";
        message.themeFontSizeJson = "";
        message.themeBreakpointsJson = "";
        if (value !== undefined)
            reflectionMergePartial(this, message, value);
        return message;
    }
    internalBinaryRead(reader, length, options, target) {
        let message = target ?? this.create(), end = reader.pos + length;
        while (reader.pos < end) {
            let [fieldNo, wireType] = reader.tag();
            switch (fieldNo) {
                case /* sads.v1.SadsElementStyles element_styles */ 1:
                    message.elementStyles = SadsElementStyles.internalBinaryRead(reader, reader.uint32(), options, message.elementStyles);
                    break;
                case /* sads.v1.SadsProcessingContext context */ 2:
                    message.context = SadsProcessingContext.internalBinaryRead(reader, reader.uint32(), options, message.context);
                    break;
                case /* string theme_colors_json */ 3:
                    message.themeColorsJson = reader.string();
                    break;
                case /* string theme_spacing_json */ 4:
                    message.themeSpacingJson = reader.string();
                    break;
                case /* string theme_font_size_json */ 5:
                    message.themeFontSizeJson = reader.string();
                    break;
                case /* string theme_breakpoints_json */ 6:
                    message.themeBreakpointsJson = reader.string();
                    break;
                default:
                    let u = options.readUnknownField;
                    if (u === "throw")
                        throw new globalThis.Error(`Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`);
                    let d = reader.skip(wireType);
                    if (u !== false)
                        (u === true ? UnknownFieldHandler.onRead : u)(this.typeName, message, fieldNo, wireType, d);
            }
        }
        return message;
    }
    internalBinaryWrite(message, writer, options) {
        /* sads.v1.SadsElementStyles element_styles = 1; */
        if (message.elementStyles)
            SadsElementStyles.internalBinaryWrite(message.elementStyles, writer.tag(1, WireType.LengthDelimited).fork(), options).join();
        /* sads.v1.SadsProcessingContext context = 2; */
        if (message.context)
            SadsProcessingContext.internalBinaryWrite(message.context, writer.tag(2, WireType.LengthDelimited).fork(), options).join();
        /* string theme_colors_json = 3; */
        if (message.themeColorsJson !== "")
            writer.tag(3, WireType.LengthDelimited).string(message.themeColorsJson);
        /* string theme_spacing_json = 4; */
        if (message.themeSpacingJson !== "")
            writer.tag(4, WireType.LengthDelimited).string(message.themeSpacingJson);
        /* string theme_font_size_json = 5; */
        if (message.themeFontSizeJson !== "")
            writer.tag(5, WireType.LengthDelimited).string(message.themeFontSizeJson);
        /* string theme_breakpoints_json = 6; */
        if (message.themeBreakpointsJson !== "")
            writer.tag(6, WireType.LengthDelimited).string(message.themeBreakpointsJson);
        let u = options.writeUnknownFields;
        if (u !== false)
            (u == true ? UnknownFieldHandler.onWrite : u)(this.typeName, message, writer);
        return writer;
    }
}
/**
 * @generated MessageType for protobuf message sads.v1.ResolveSadsStylesRequest
 */
export const ResolveSadsStylesRequest = new ResolveSadsStylesRequest$Type();
// @generated message type with reflection information, may provide speed optimized methods
class ResolveSadsStylesResponse$Type extends MessageType {
    constructor() {
        super("sads.v1.ResolveSadsStylesResponse", [
            { no: 1, name: "css_rules", kind: "scalar", T: 9 /*ScalarType.STRING*/ }
        ]);
    }
    create(value) {
        const message = globalThis.Object.create((this.messagePrototype));
        message.cssRules = "";
        if (value !== undefined)
            reflectionMergePartial(this, message, value);
        return message;
    }
    internalBinaryRead(reader, length, options, target) {
        let message = target ?? this.create(), end = reader.pos + length;
        while (reader.pos < end) {
            let [fieldNo, wireType] = reader.tag();
            switch (fieldNo) {
                case /* string css_rules */ 1:
                    message.cssRules = reader.string();
                    break;
                default:
                    let u = options.readUnknownField;
                    if (u === "throw")
                        throw new globalThis.Error(`Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`);
                    let d = reader.skip(wireType);
                    if (u !== false)
                        (u === true ? UnknownFieldHandler.onRead : u)(this.typeName, message, fieldNo, wireType, d);
            }
        }
        return message;
    }
    internalBinaryWrite(message, writer, options) {
        /* string css_rules = 1; */
        if (message.cssRules !== "")
            writer.tag(1, WireType.LengthDelimited).string(message.cssRules);
        let u = options.writeUnknownFields;
        if (u !== false)
            (u == true ? UnknownFieldHandler.onWrite : u)(this.typeName, message, writer);
        return writer;
    }
}
/**
 * @generated MessageType for protobuf message sads.v1.ResolveSadsStylesResponse
 */
export const ResolveSadsStylesResponse = new ResolveSadsStylesResponse$Type();
//# sourceMappingURL=sads_styling.v1.js.map