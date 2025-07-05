import { WireType } from "@protobuf-ts/runtime";
import { UnknownFieldHandler } from "@protobuf-ts/runtime";
import { reflectionMergePartial } from "@protobuf-ts/runtime";
import { MessageType } from "@protobuf-ts/runtime";
import { Image } from "./common";
import { I18nString } from "./common";
// @generated message type with reflection information, may provide speed optimized methods
class TestimonialItem$Type extends MessageType {
  constructor() {
    super("website_content.v1.TestimonialItem", [
      { no: 1, name: "text", kind: "message", T: () => I18nString },
      { no: 2, name: "author", kind: "message", T: () => I18nString },
      { no: 3, name: "author_image", kind: "message", T: () => Image },
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
        case /* website_content.v1.I18nString text */ 1:
          message.text = I18nString.internalBinaryRead(
            reader,
            reader.uint32(),
            options,
            message.text
          );
          break;
        case /* website_content.v1.I18nString author */ 2:
          message.author = I18nString.internalBinaryRead(
            reader,
            reader.uint32(),
            options,
            message.author
          );
          break;
        case /* website_content.v1.Image author_image */ 3:
          message.authorImage = Image.internalBinaryRead(
            reader,
            reader.uint32(),
            options,
            message.authorImage
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
    /* website_content.v1.I18nString text = 1; */
    if (message.text)
      I18nString.internalBinaryWrite(
        message.text,
        writer.tag(1, WireType.LengthDelimited).fork(),
        options
      ).join();
    /* website_content.v1.I18nString author = 2; */
    if (message.author)
      I18nString.internalBinaryWrite(
        message.author,
        writer.tag(2, WireType.LengthDelimited).fork(),
        options
      ).join();
    /* website_content.v1.Image author_image = 3; */
    if (message.authorImage)
      Image.internalBinaryWrite(
        message.authorImage,
        writer.tag(3, WireType.LengthDelimited).fork(),
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
 * @generated MessageType for protobuf message website_content.v1.TestimonialItem
 */
export const TestimonialItem = new TestimonialItem$Type();
//# sourceMappingURL=testimonial_item.js.map
