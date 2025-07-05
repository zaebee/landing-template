import { WireType } from "@protobuf-ts/runtime";
import { UnknownFieldHandler } from "@protobuf-ts/runtime";
import { reflectionMergePartial } from "@protobuf-ts/runtime";
import { MessageType } from "@protobuf-ts/runtime";
// @generated message type with reflection information, may provide speed optimized methods
class I18nString$Type extends MessageType {
  constructor() {
    super("website_content.v1.I18nString", [
      { no: 1, name: "key", kind: "scalar", T: 9 /*ScalarType.STRING*/ },
    ]);
  }
  create(value) {
    const message = globalThis.Object.create(this.messagePrototype);
    message.key = "";
    if (value !== undefined) reflectionMergePartial(this, message, value);
    return message;
  }
  internalBinaryRead(reader, length, options, target) {
    let message = target ?? this.create(),
      end = reader.pos + length;
    while (reader.pos < end) {
      let [fieldNo, wireType] = reader.tag();
      switch (fieldNo) {
        case /* string key */ 1:
          message.key = reader.string();
          break;
        default:
          let u = options.readUnknownField;
          if (u === "throw")
            throw new globalThis.Error(
              `Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`
            );
          let d = reader.skip(wireType);
          if (u !== false)
            (u === true ? UnknownFieldHandler.onRead : u)(
              this.typeName,
              message,
              fieldNo,
              wireType,
              d
            );
      }
    }
    return message;
  }
  internalBinaryWrite(message, writer, options) {
    /* string key = 1; */
    if (message.key !== "")
      writer.tag(1, WireType.LengthDelimited).string(message.key);
    let u = options.writeUnknownFields;
    if (u !== false)
      (u == true ? UnknownFieldHandler.onWrite : u)(
        this.typeName,
        message,
        writer
      );
    return writer;
  }
}
/**
 * @generated MessageType for protobuf message website_content.v1.I18nString
 */
export const I18nString = new I18nString$Type();
// @generated message type with reflection information, may provide speed optimized methods
class Image$Type extends MessageType {
  constructor() {
    super("website_content.v1.Image", [
      { no: 1, name: "src", kind: "scalar", T: 9 /*ScalarType.STRING*/ },
      { no: 2, name: "alt_text", kind: "message", T: () => I18nString },
    ]);
  }
  create(value) {
    const message = globalThis.Object.create(this.messagePrototype);
    message.src = "";
    if (value !== undefined) reflectionMergePartial(this, message, value);
    return message;
  }
  internalBinaryRead(reader, length, options, target) {
    let message = target ?? this.create(),
      end = reader.pos + length;
    while (reader.pos < end) {
      let [fieldNo, wireType] = reader.tag();
      switch (fieldNo) {
        case /* string src */ 1:
          message.src = reader.string();
          break;
        case /* website_content.v1.I18nString alt_text */ 2:
          message.altText = I18nString.internalBinaryRead(
            reader,
            reader.uint32(),
            options,
            message.altText
          );
          break;
        default:
          let u = options.readUnknownField;
          if (u === "throw")
            throw new globalThis.Error(
              `Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`
            );
          let d = reader.skip(wireType);
          if (u !== false)
            (u === true ? UnknownFieldHandler.onRead : u)(
              this.typeName,
              message,
              fieldNo,
              wireType,
              d
            );
      }
    }
    return message;
  }
  internalBinaryWrite(message, writer, options) {
    /* string src = 1; */
    if (message.src !== "")
      writer.tag(1, WireType.LengthDelimited).string(message.src);
    /* website_content.v1.I18nString alt_text = 2; */
    if (message.altText)
      I18nString.internalBinaryWrite(
        message.altText,
        writer.tag(2, WireType.LengthDelimited).fork(),
        options
      ).join();
    let u = options.writeUnknownFields;
    if (u !== false)
      (u == true ? UnknownFieldHandler.onWrite : u)(
        this.typeName,
        message,
        writer
      );
    return writer;
  }
}
/**
 * @generated MessageType for protobuf message website_content.v1.Image
 */
export const Image = new Image$Type();
// @generated message type with reflection information, may provide speed optimized methods
class CTA$Type extends MessageType {
  constructor() {
    super("website_content.v1.CTA", [
      { no: 1, name: "text", kind: "message", T: () => I18nString },
      { no: 2, name: "uri", kind: "scalar", T: 9 /*ScalarType.STRING*/ },
    ]);
  }
  create(value) {
    const message = globalThis.Object.create(this.messagePrototype);
    message.uri = "";
    if (value !== undefined) reflectionMergePartial(this, message, value);
    return message;
  }
  internalBinaryRead(reader, length, options, target) {
    let message = target ?? this.create(),
      end = reader.pos + length;
    while (reader.pos < end) {
      let [fieldNo, wireType] = reader.tag();
      switch (fieldNo) {
        case /* website_content.v1.I18nString text */ 1:
          message.text = I18nString.internalBinaryRead(
            reader,
            reader.uint32(),
            options,
            message.text
          );
          break;
        case /* string uri */ 2:
          message.uri = reader.string();
          break;
        default:
          let u = options.readUnknownField;
          if (u === "throw")
            throw new globalThis.Error(
              `Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`
            );
          let d = reader.skip(wireType);
          if (u !== false)
            (u === true ? UnknownFieldHandler.onRead : u)(
              this.typeName,
              message,
              fieldNo,
              wireType,
              d
            );
      }
    }
    return message;
  }
  internalBinaryWrite(message, writer, options) {
    /* website_content.v1.I18nString text = 1; */
    if (message.text)
      I18nString.internalBinaryWrite(
        message.text,
        writer.tag(1, WireType.LengthDelimited).fork(),
        options
      ).join();
    /* string uri = 2; */
    if (message.uri !== "")
      writer.tag(2, WireType.LengthDelimited).string(message.uri);
    let u = options.writeUnknownFields;
    if (u !== false)
      (u == true ? UnknownFieldHandler.onWrite : u)(
        this.typeName,
        message,
        writer
      );
    return writer;
  }
}
/**
 * @generated MessageType for protobuf message website_content.v1.CTA
 */
export const CTA = new CTA$Type();
// @generated message type with reflection information, may provide speed optimized methods
class TitledBlock$Type extends MessageType {
  constructor() {
    super("website_content.v1.TitledBlock", [
      { no: 1, name: "title", kind: "message", T: () => I18nString },
      { no: 2, name: "description", kind: "message", T: () => I18nString },
    ]);
  }
  create(value) {
    const message = globalThis.Object.create(this.messagePrototype);
    if (value !== undefined) reflectionMergePartial(this, message, value);
    return message;
  }
  internalBinaryRead(reader, length, options, target) {
    let message = target ?? this.create(),
      end = reader.pos + length;
    while (reader.pos < end) {
      let [fieldNo, wireType] = reader.tag();
      switch (fieldNo) {
        case /* website_content.v1.I18nString title */ 1:
          message.title = I18nString.internalBinaryRead(
            reader,
            reader.uint32(),
            options,
            message.title
          );
          break;
        case /* website_content.v1.I18nString description */ 2:
          message.description = I18nString.internalBinaryRead(
            reader,
            reader.uint32(),
            options,
            message.description
          );
          break;
        default:
          let u = options.readUnknownField;
          if (u === "throw")
            throw new globalThis.Error(
              `Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`
            );
          let d = reader.skip(wireType);
          if (u !== false)
            (u === true ? UnknownFieldHandler.onRead : u)(
              this.typeName,
              message,
              fieldNo,
              wireType,
              d
            );
      }
    }
    return message;
  }
  internalBinaryWrite(message, writer, options) {
    /* website_content.v1.I18nString title = 1; */
    if (message.title)
      I18nString.internalBinaryWrite(
        message.title,
        writer.tag(1, WireType.LengthDelimited).fork(),
        options
      ).join();
    /* website_content.v1.I18nString description = 2; */
    if (message.description)
      I18nString.internalBinaryWrite(
        message.description,
        writer.tag(2, WireType.LengthDelimited).fork(),
        options
      ).join();
    let u = options.writeUnknownFields;
    if (u !== false)
      (u == true ? UnknownFieldHandler.onWrite : u)(
        this.typeName,
        message,
        writer
      );
    return writer;
  }
}
/**
 * @generated MessageType for protobuf message website_content.v1.TitledBlock
 */
export const TitledBlock = new TitledBlock$Type();
// @generated message type with reflection information, may provide speed optimized methods
class SiteLogo$Type extends MessageType {
  constructor() {
    super("website_content.v1.SiteLogo", [
      { no: 1, name: "image_path", kind: "scalar", T: 9 /*ScalarType.STRING*/ },
      {
        no: 2,
        name: "alt_text_key",
        kind: "scalar",
        T: 9 /*ScalarType.STRING*/,
      },
      {
        no: 3,
        name: "logo_text_key",
        kind: "scalar",
        T: 9 /*ScalarType.STRING*/,
      },
      { no: 4, name: "target_url", kind: "scalar", T: 9 /*ScalarType.STRING*/ },
    ]);
  }
  create(value) {
    const message = globalThis.Object.create(this.messagePrototype);
    message.imagePath = "";
    message.altTextKey = "";
    message.logoTextKey = "";
    message.targetUrl = "";
    if (value !== undefined) reflectionMergePartial(this, message, value);
    return message;
  }
  internalBinaryRead(reader, length, options, target) {
    let message = target ?? this.create(),
      end = reader.pos + length;
    while (reader.pos < end) {
      let [fieldNo, wireType] = reader.tag();
      switch (fieldNo) {
        case /* string image_path */ 1:
          message.imagePath = reader.string();
          break;
        case /* string alt_text_key */ 2:
          message.altTextKey = reader.string();
          break;
        case /* string logo_text_key */ 3:
          message.logoTextKey = reader.string();
          break;
        case /* string target_url */ 4:
          message.targetUrl = reader.string();
          break;
        default:
          let u = options.readUnknownField;
          if (u === "throw")
            throw new globalThis.Error(
              `Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`
            );
          let d = reader.skip(wireType);
          if (u !== false)
            (u === true ? UnknownFieldHandler.onRead : u)(
              this.typeName,
              message,
              fieldNo,
              wireType,
              d
            );
      }
    }
    return message;
  }
  internalBinaryWrite(message, writer, options) {
    /* string image_path = 1; */
    if (message.imagePath !== "")
      writer.tag(1, WireType.LengthDelimited).string(message.imagePath);
    /* string alt_text_key = 2; */
    if (message.altTextKey !== "")
      writer.tag(2, WireType.LengthDelimited).string(message.altTextKey);
    /* string logo_text_key = 3; */
    if (message.logoTextKey !== "")
      writer.tag(3, WireType.LengthDelimited).string(message.logoTextKey);
    /* string target_url = 4; */
    if (message.targetUrl !== "")
      writer.tag(4, WireType.LengthDelimited).string(message.targetUrl);
    let u = options.writeUnknownFields;
    if (u !== false)
      (u == true ? UnknownFieldHandler.onWrite : u)(
        this.typeName,
        message,
        writer
      );
    return writer;
  }
}
/**
 * @generated MessageType for protobuf message website_content.v1.SiteLogo
 */
export const SiteLogo = new SiteLogo$Type();
//# sourceMappingURL=common.js.map
