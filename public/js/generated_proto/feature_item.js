import { WireType } from "@protobuf-ts/runtime";
import { UnknownFieldHandler } from "@protobuf-ts/runtime";
import { reflectionMergePartial } from "@protobuf-ts/runtime";
import { MessageType } from "@protobuf-ts/runtime";
import { TitledBlock } from "./common";
// @generated message type with reflection information, may provide speed optimized methods
class FeatureItem$Type extends MessageType {
    constructor() {
        super("website_content.v1.FeatureItem", [
            { no: 1, name: "content", kind: "message", T: () => TitledBlock }
        ]);
    }
    create(value) {
        const message = globalThis.Object.create((this.messagePrototype));
        if (value !== undefined)
            reflectionMergePartial(this, message, value);
        return message;
    }
    internalBinaryRead(reader, length, options, target) {
        let message = target ?? this.create(), end = reader.pos + length;
        while (reader.pos < end) {
            let [fieldNo, wireType] = reader.tag();
            switch (fieldNo) {
                case /* website_content.v1.TitledBlock content */ 1:
                    message.content = TitledBlock.internalBinaryRead(reader, reader.uint32(), options, message.content);
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
        /* website_content.v1.TitledBlock content = 1; */
        if (message.content)
            TitledBlock.internalBinaryWrite(message.content, writer.tag(1, WireType.LengthDelimited).fork(), options).join();
        let u = options.writeUnknownFields;
        if (u !== false)
            (u == true ? UnknownFieldHandler.onWrite : u)(this.typeName, message, writer);
        return writer;
    }
}
/**
 * @generated MessageType for protobuf message website_content.v1.FeatureItem
 */
export const FeatureItem = new FeatureItem$Type();
//# sourceMappingURL=feature_item.js.map